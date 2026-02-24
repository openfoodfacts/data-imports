#!/usr/bin/env python3
"""Rappel Conso daily import script.

Fetches food product recall data from the French Rappel Conso database,
checks if each product (identified by GTIN/barcode) already exists in
Open Food Facts, and writes a CSV of new products suitable for OFF import.

The script is designed to run daily, processing only recalls published
since the previous day by default.

Usage:
    # Process recalls from the last day (default, for daily cron)
    python import_rappelconso.py --output ../data/

    # Process recalls since a specific date
    python import_rappelconso.py --since 2024-11-29 --output ../data/

    # Look back N days
    python import_rappelconso.py --days 7 --output ../data/

    # Skip the OFF existence check (output all food products with GTINs)
    python import_rappelconso.py --no-off-check --output ../data/
"""

import argparse
import csv
import logging
import os
import sys
from datetime import date, timedelta

import requests

from rappelconso_client import RappelConsoClient, FOOD_CATEGORY

logger = logging.getLogger(__name__)

OFF_API_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

OFF_CSV_HEADERS = [
    "code",
    "product_name",
    "brands",
    "categories",
    "countries",
    "source",
    "rappelconso:fiche_id",
    "rappelconso:lien_fiche",
]


def check_off_product_exists(barcode, session=None):
    """Check if a product exists in Open Food Facts.

    Args:
        barcode: Product barcode/GTIN string.
        session: Optional requests.Session to reuse for connection pooling.

    Returns:
        True if the product exists in OFF, False if it does not,
        None if the check could not be completed.
    """
    url = OFF_API_URL.format(barcode=barcode)
    try:
        s = session or requests
        response = s.get(
            url, timeout=10, headers={"Accept": "application/json"}
        )
        if response.status_code == 404:
            return False
        response.raise_for_status()
        data = response.json()
        return data.get("status") == 1
    except requests.exceptions.RequestException as e:
        logger.warning(
            "Failed to check OFF for barcode %s: %s", barcode, e
        )
        return None


def extract_gtins(identification_produits):
    """Extract GTINs from the identification_produits field.

    The field is a list (from the JSON API) where each product recall group
    has the format: [GTIN, lot_number, date_type, date_start, (date_end)].
    Multiple groups are separated by a standalone "|" element; when the
    next group HAS a GTIN, the "|" is prepended to it (e.g. "|3760001234567").

    Args:
        identification_produits: List (from API) or None.

    Returns:
        List of GTIN strings (digits only, length 8-14).
    """
    if not identification_produits:
        return []

    gtins = []
    items = list(identification_produits) if not isinstance(
        identification_produits, list
    ) else identification_produits

    for i, value in enumerate(items):
        val = str(value).strip() if value else ""
        if i == 0:
            # First element of the first group is always the GTIN (may be "")
            candidate = val
        elif val.startswith("|"):
            # Group separator: strip "|" to get GTIN of the next group
            candidate = val[1:].strip()
        else:
            continue

        if candidate.isdigit() and 8 <= len(candidate) <= 14:
            gtins.append(candidate)

    return gtins


def build_off_row(record, gtin):
    """Build an OFF import CSV row from a Rappel Conso record.

    Only product identification data is included; recall-specific data
    (reason for recall, risk description, etc.) is intentionally excluded.

    Args:
        record: Rappel Conso recall record dict.
        gtin: Specific GTIN/barcode for this product row.

    Returns:
        Dict with OFF import fields.
    """
    brand = (record.get("marque_produit") or "").strip()
    product_name = (
        (record.get("libelle") or "").strip()
        or (record.get("modeles_ou_references") or "").strip()
        or brand
    )
    category = (
        (record.get("sous_categorie_produit") or "").strip()
        or (record.get("categorie_produit") or "").strip()
    )

    return {
        "code": gtin,
        "product_name": product_name,
        "brands": brand,
        "categories": category,
        "countries": "France",
        "source": "Rappel Conso",
        "rappelconso:fiche_id": str(record.get("id", "")),
        "rappelconso:lien_fiche": record.get(
            "lien_vers_la_fiche_rappel", ""
        ),
    }


def process_recalls(client, since_date=None, check_off=True,
                    off_session=None):
    """Process Rappel Conso records and yield new food products for OFF.

    Fetches food-category recalls, extracts GTINs, deduplicates them,
    and optionally filters out products that already exist in OFF.

    Args:
        client: RappelConsoClient instance.
        since_date: Only process recalls published on or after this date.
        check_off: If True, check the OFF API before yielding each product.
        off_session: Optional requests.Session for OFF API calls.

    Yields:
        Dict rows for products not yet in OFF (or all products if
        check_off is False).
    """
    seen_gtins = set()

    for record in client.fetch_all_recalls(
        since_date=since_date, category=FOOD_CATEGORY
    ):
        gtin_field = record.get("identification_produits", [])
        gtins = extract_gtins(gtin_field)

        if not gtins:
            logger.debug(
                "No GTIN for record %s", record.get("id", "?")
            )
            continue

        for gtin in gtins:
            if gtin in seen_gtins:
                continue
            seen_gtins.add(gtin)

            if check_off:
                exists = check_off_product_exists(gtin, session=off_session)
                if exists is True:
                    logger.debug(
                        "Product %s already exists in OFF", gtin
                    )
                    continue
                if exists is None:
                    logger.warning(
                        "Could not check OFF for %s, skipping", gtin
                    )
                    continue

            yield build_off_row(record, gtin)


def save_csv(rows, output_path):
    """Save product rows to a CSV file for OFF import.

    Args:
        rows: Iterable of row dicts with OFF import fields.
        output_path: Destination file path.

    Returns:
        Number of rows written.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    count = 0

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=OFF_CSV_HEADERS, extrasaction="ignore"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1

    logger.info("Wrote %d products to %s", count, output_path)
    return count


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Rappel Conso recall data and identify new food "
            "products for Open Food Facts import."
        ),
    )

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        "--since",
        metavar="DATE",
        help=(
            "Only process recalls published on or after this date "
            "(YYYY-MM-DD)."
        ),
    )
    date_group.add_argument(
        "--days",
        type=int,
        default=1,
        help=(
            "Number of days to look back from today (default: 1). "
            "Use this for scheduled daily imports."
        ),
    )

    parser.add_argument(
        "--output",
        default=os.path.join(os.path.dirname(__file__), "..", "data"),
        help="Output directory for CSV files (default: ../data/).",
    )
    parser.add_argument(
        "--no-off-check",
        action="store_true",
        default=False,
        help=(
            "Skip checking Open Food Facts API (output all food products "
            "with GTINs, regardless of whether they exist in OFF)."
        ),
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Enable verbose/debug logging.",
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

    if args.since:
        since_date = args.since
    else:
        since_date = (date.today() - timedelta(days=args.days)).isoformat()

    logger.info("Processing recalls since %s", since_date)

    os.makedirs(args.output, exist_ok=True)
    output_path = os.path.join(
        args.output,
        f"rappelconso_new_products_{date.today().isoformat()}.csv",
    )

    off_session = None
    count = 0
    with RappelConsoClient() as client:
        if not args.no_off_check:
            off_session = requests.Session()
        try:
            rows = process_recalls(
                client,
                since_date=since_date,
                check_off=not args.no_off_check,
                off_session=off_session,
            )
            count = save_csv(rows, output_path)
        finally:
            if off_session:
                off_session.close()

    logger.info("Done. Found %d new food products.", count)
    print(f"Output: {output_path} ({count} new products)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
