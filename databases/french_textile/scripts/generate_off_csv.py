#!/usr/bin/env python3
"""Generate Open Products Facts core import CSV from French textile data.

Produces a CSV with fields suitable for direct import into Open Products Facts:
- code (barcode / GTIN)
- product_name_fr (from "Référence interne")
- brands (from "Marque")
- categories (mapped to OFF taxonomy)
- labels (environmental and durability scores)
- url (link to ecobalyse product page)
"""

import argparse
import csv
import os
import sys
import urllib.request

from field_mapping import CATEGORY_MAP, DATA_SOURCE_URL, ECOBALYSE_BASE_URL


def download_source(output_path):
    """Download the source CSV from data.gouv.fr."""
    print(f"Downloading data from {DATA_SOURCE_URL}...")
    urllib.request.urlretrieve(DATA_SOURCE_URL, output_path)
    print(f"Downloaded to {output_path}")


def build_labels(row):
    """Build labels string from score and durability values.

    Format:
    - "en:Score Environnemental <rounded standardized score>"
    - "en:Score de Durabilité <durability as percentage>%"
    """
    labels = []

    standardized_score = row.get("Score standardisé", "").strip()
    if standardized_score:
        try:
            score_val = float(standardized_score)
            labels.append(f"en:Score Environnemental {round(score_val)}")
        except ValueError:
            pass

    durability = row.get("Durabilité", "").strip()
    if durability:
        try:
            dur_val = float(durability)
            dur_pct = round(dur_val * 100)
            labels.append(f"en:Score de Durabilité {dur_pct}%")
        except ValueError:
            pass

    return ",".join(labels)


def map_category(french_category):
    """Map a French textile category to an OFF taxonomy category."""
    mapped = CATEGORY_MAP.get(french_category)
    if not mapped:
        print(
            f"Warning: unmapped category '{french_category}'",
            file=sys.stderr,
        )
        return french_category
    return mapped


def generate_off_csv(input_path, output_path):
    """Read source CSV and write OFF core import CSV."""
    fieldnames = [
        "code",
        "product_name_fr",
        "brands",
        "categories",
        "labels",
        "url",
    ]

    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            count = 0
            for row in reader:
                gtin = row.get("GTIN", "").strip()
                code = gtin if gtin else f"textile_{count}"

                off_row = {
                    "code": code,
                    "product_name_fr": row.get("Référence interne", "").strip(),
                    "brands": row.get("Marque", "").strip(),
                    "categories": map_category(
                        row.get("Catégorie", "").strip()
                    ),
                    "labels": build_labels(row),
                    "url": f"{ECOBALYSE_BASE_URL}{code}",
                }
                writer.writerow(off_row)
                count += 1

    print(f"Wrote {count} rows to {output_path}")
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Generate OFF core import CSV from French textile data"
    )
    parser.add_argument(
        "--input",
        help="Path to source CSV (will download if not provided)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(
            os.path.dirname(__file__), "..", "data", "off_core_import.csv"
        ),
        help="Path to output CSV",
    )
    args = parser.parse_args()

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)

    if args.input:
        input_path = args.input
    else:
        input_path = os.path.join(data_dir, "source.csv")
        if not os.path.exists(input_path):
            download_source(input_path)

    generate_off_csv(input_path, args.output)


if __name__ == "__main__":
    main()
