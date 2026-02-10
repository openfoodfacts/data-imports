#!/usr/bin/env python3
"""EPREL data ingestion script.

Fetches product data from the EU EPREL (European Product Registry for Energy
Labelling) API and stores it as JSON or CSV files for later import into
Open Products Facts.

Usage:
    python import_eprel.py --category smartphones --output ../data/
    python import_eprel.py --category smartphones --api-key KEY --output ../data/
    python import_eprel.py --category smartphones --max-pages 5 --output ../data/
    python import_eprel.py --category smartphones --format csv --output ../data/
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime, timezone

from eprel_client import EPRELClient, PRODUCT_CATEGORIES
from field_mapping import map_product_fields, get_opf_csv_headers

logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the script."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def fetch_and_save(client, category, output_dir, max_pages=None,
                   page_size=50, fetch_details=False, output_format="json"):
    """Fetch products from a category and save to a JSON or CSV file.

    Args:
        client: An EPRELClient instance.
        category: Product category key.
        output_dir: Directory to write output files.
        max_pages: Maximum number of listing pages to fetch.
        page_size: Number of results per listing page.
        fetch_details: If True, fetch full details for each product.
        output_format: "json" or "csv". CSV uses OPF field names.

    Returns:
        Path to the written output file.
    """
    os.makedirs(output_dir, exist_ok=True)

    all_product_ids = []
    for page_hits in client.fetch_all_products(
        category, max_pages=max_pages, page_size=page_size
    ):
        all_product_ids.extend(page_hits)

    logger.info(
        "Found %d product IDs for category '%s'",
        len(all_product_ids), category,
    )

    products = []
    if fetch_details:
        for i, eprel_id in enumerate(all_product_ids):
            try:
                product = client.get_product(category, eprel_id)
                products.append(product)
                if (i + 1) % 100 == 0:
                    logger.info(
                        "Fetched details for %d/%d products",
                        i + 1, len(all_product_ids),
                    )
            except Exception:
                logger.exception(
                    "Failed to fetch product %s", eprel_id
                )
    else:
        products = [{"eprelRegistrationNumber": pid}
                    for pid in all_product_ids]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if output_format == "csv":
        return _save_csv(products, category, timestamp, output_dir)
    return _save_json(products, category, timestamp, output_dir,
                      fetch_details)


def _save_json(products, category, timestamp, output_dir, fetch_details):
    """Save products as a JSON file with metadata."""
    filename = f"eprel_{category}_{timestamp}.json"
    output_path = os.path.join(output_dir, filename)

    output_data = {
        "source": "EPREL",
        "category": category,
        "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_products": len(products),
        "details_fetched": fetch_details,
        "products": products,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info("Saved %d products to %s", len(products), output_path)
    return output_path


def _save_csv(products, category, timestamp, output_dir):
    """Save products as a CSV file with OPF field names."""
    filename = f"eprel_{category}_{timestamp}.csv"
    output_path = os.path.join(output_dir, filename)

    mapped_products = [map_product_fields(p) for p in products]

    # Collect all field names across all products
    all_fields = set()
    for p in mapped_products:
        all_fields.update(p.keys())
    headers = sorted(all_fields)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(mapped_products)

    logger.info(
        "Saved %d products (CSV, OPF field names) to %s",
        len(mapped_products), output_path,
    )
    return output_path


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch product data from the EU EPREL database.",
    )
    parser.add_argument(
        "--category",
        action="append",
        dest="categories",
        choices=sorted(PRODUCT_CATEGORIES.keys()),
        required=True,
        help="Product category to fetch (can be specified multiple times).",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("EPREL_API_KEY"),
        help="EPREL API key (or set EPREL_API_KEY environment variable).",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(os.path.dirname(__file__), "..", "data"),
        help="Output directory for JSON files (default: ../data/).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum number of listing pages to fetch per category.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Number of results per listing page (default: 50).",
    )
    parser.add_argument(
        "--fetch-details",
        action="store_true",
        default=False,
        help=(
            "Fetch full product details "
            "(slower, makes one request per product)."
        ),
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        dest="output_format",
        help=(
            "Output format: json (raw EPREL fields) or csv "
            "(OPF field names). Default: json."
        ),
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
    setup_logging(args.verbose)

    with EPRELClient(api_key=args.api_key) as client:
        for category in args.categories:
            logger.info("Processing category: %s", category)
            try:
                fetch_and_save(
                    client,
                    category,
                    args.output,
                    max_pages=args.max_pages,
                    page_size=args.page_size,
                    fetch_details=args.fetch_details,
                    output_format=args.output_format,
                )
            except Exception:
                logger.exception(
                    "Failed to process category '%s'", category
                )

    logger.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
