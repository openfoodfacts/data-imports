#!/usr/bin/env python3
"""Generate a CSV suitable for Open Food Facts core import from EPREL data.

Reads an EPREL CSV (with OPF field names) or raw EPREL product data and
produces a CSV with fields compatible with the Open Food Facts import
mechanism: code (barcode), product_name, brands, categories, labels, and
selected technical fields.

Since EPREL does not provide barcodes/GTINs, a placeholder barcode is
generated as "eprel_<eprel_id>" for each product.

Usage:
    python generate_off_csv.py --input ../data/eprel_smartphones_sample.csv \
        --output ../data/eprel_smartphones_off_import.csv

    python generate_off_csv.py --from-eprel-api --category smartphones \
        --api-key KEY --output ../data/eprel_smartphones_off_import.csv
"""

import argparse
import csv
import io
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)


# Labels derived from EPREL data
def _build_labels(row):
    """Build a comma-separated labels string from EPREL fields."""
    labels = ["eu:energy-labelling"]

    energy_class = row.get("energy_efficiency_class:eu", "")
    if energy_class:
        labels.append(f"eu:energy-class-{energy_class.lower()}")

    repair_class = row.get("repairability_class:eu", "")
    if repair_class:
        labels.append(f"eu:repairability-class-{repair_class.lower()}")

    return ", ".join(labels)


def _build_product_name(row):
    """Build a product name from brand and model."""
    brand = row.get("brands", "")
    model = row.get("manufacturer:reference_number", "")
    if brand and model:
        return f"{brand} {model}"
    return brand or model or ""


def _build_categories(row):
    """Build categories string from device type."""
    device_type = row.get("device_type", "")
    os_name = row.get("consumer_electronics:initial_operating_system", "")

    categories = []
    if device_type:
        dtype = device_type.strip()
        if dtype.upper() == "SMARTPHONE":
            categories.append("Smartphones")
        elif dtype.upper() == "TABLET":
            categories.append("Tablets")
        else:
            categories.append(dtype.replace("_", " ").title())

    if os_name:
        os_lower = os_name.strip().lower()
        if os_lower == "android":
            categories.append("Android smartphones")
        elif os_lower == "ios":
            categories.append("iOS smartphones")

    return ", ".join(categories) if categories else "Electronics"


def _build_barcode(row):
    """Generate barcode: use real GTIN if present, else eprel_<id>."""
    # Check for any GTIN/barcode field
    for field in ("code", "barcode", "gtin"):
        val = row.get(field, "").strip()
        if val:
            return val
    # Fall back to EPREL ID placeholder
    eprel_id = row.get("eprel_id", "")
    if eprel_id:
        return f"eprel_{eprel_id}"
    return ""


def convert_to_off_row(row):
    """Convert a single OPF-mapped row to OFF core import format.

    Args:
        row: Dict with OPF field names (from EPREL mapped CSV).

    Returns:
        Dict with OFF core import fields.
    """
    return {
        "code": _build_barcode(row),
        "product_name": _build_product_name(row),
        "brands": row.get("brands", ""),
        "categories": _build_categories(row),
        "labels": _build_labels(row),
        "energy_efficiency_class:eu": row.get(
            "energy_efficiency_class:eu", ""
        ),
        "repairability_class:eu": row.get("repairability_class:eu", ""),
        "repairability_index:eu": row.get("repairability_index:eu", ""),
        "consumer_electronics:battery_capacity:mah": row.get(
            "consumer_electronics:battery_capacity:mah", ""
        ),
        "consumer_electronics:initial_operating_system": row.get(
            "consumer_electronics:initial_operating_system", ""
        ),
        "ingress_protection_rating:ip:number": row.get(
            "ingress_protection_rating:ip:number", ""
        ),
        "repeated_free_fall_reliability_class:eu": row.get(
            "repeated_free_fall_reliability_class:eu", ""
        ),
        "ec_energy_label:url": row.get("ec_energy_label:url", ""),
        "ec_energy_label:svg_url": row.get("ec_energy_label:svg_url", ""),
        "release_date": row.get("release_date", ""),
    }


OFF_CORE_HEADERS = [
    "code",
    "product_name",
    "brands",
    "categories",
    "labels",
    "energy_efficiency_class:eu",
    "repairability_class:eu",
    "repairability_index:eu",
    "consumer_electronics:battery_capacity:mah",
    "consumer_electronics:initial_operating_system",
    "ingress_protection_rating:ip:number",
    "repeated_free_fall_reliability_class:eu",
    "ec_energy_label:url",
    "ec_energy_label:svg_url",
    "release_date",
]


def convert_csv(input_path, output_path):
    """Read an OPF-mapped EPREL CSV and write an OFF core import CSV.

    Args:
        input_path: Path to input CSV with OPF field names.
        output_path: Path for the output OFF core CSV.

    Returns:
        Number of products written.
    """
    with open(input_path, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = [convert_to_off_row(row) for row in reader]

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(
            fout, fieldnames=OFF_CORE_HEADERS, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Wrote %d products to %s", len(rows), output_path)
    return len(rows)


def convert_json_products(products, output_path):
    """Convert a list of OPF-mapped product dicts to OFF core CSV.

    Args:
        products: List of dicts with OPF field names.
        output_path: Path for the output OFF core CSV.

    Returns:
        Number of products written.
    """
    rows = [convert_to_off_row(p) for p in products]

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(
            fout, fieldnames=OFF_CORE_HEADERS, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Wrote %d products to %s", len(rows), output_path)
    return len(rows)


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate an Open Food Facts core import CSV from EPREL data."
        ),
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to an OPF-mapped EPREL CSV file.",
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Path for the output OFF core CSV file.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Enable verbose logging.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Main entry point."""
    args = parse_args(argv)
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    count = convert_csv(args.input, args.output)
    print(f"Converted {count} products to OFF core format: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
