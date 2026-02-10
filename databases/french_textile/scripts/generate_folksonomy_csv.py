#!/usr/bin/env python3
"""Generate Folksonomy Engine CSV from French textile environmental cost data.

Downloads the raw CSV from data.gouv.fr and renames columns to
folksonomy-style hierarchical field names (textile:french_environmental_cost:*).
"""

import argparse
import csv
import os
import sys
import urllib.request

from field_mapping import DATA_SOURCE_URL, FOLKSONOMY_FIELD_MAP


def download_source(output_path):
    """Download the source CSV from data.gouv.fr."""
    print(f"Downloading data from {DATA_SOURCE_URL}...")
    urllib.request.urlretrieve(DATA_SOURCE_URL, output_path)
    print(f"Downloaded to {output_path}")


def generate_folksonomy_csv(input_path, output_path):
    """Read source CSV and write folksonomy CSV with renamed columns."""
    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # Build renamed fieldnames
        renamed_fields = []
        for field in reader.fieldnames:
            if field in FOLKSONOMY_FIELD_MAP:
                renamed_fields.append(FOLKSONOMY_FIELD_MAP[field])
            else:
                print(f"Warning: unmapped field '{field}'", file=sys.stderr)
                renamed_fields.append(field)

        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=renamed_fields)
            writer.writeheader()

            count = 0
            for row in reader:
                renamed_row = {}
                for orig_key, value in row.items():
                    new_key = FOLKSONOMY_FIELD_MAP.get(orig_key, orig_key)
                    renamed_row[new_key] = value
                writer.writerow(renamed_row)
                count += 1

    print(f"Wrote {count} rows to {output_path}")
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Generate Folksonomy Engine CSV from French textile data"
    )
    parser.add_argument(
        "--input",
        help="Path to source CSV (will download if not provided)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(
            os.path.dirname(__file__), "..", "data", "folksonomy_import.csv"
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

    generate_folksonomy_csv(input_path, args.output)


if __name__ == "__main__":
    main()
