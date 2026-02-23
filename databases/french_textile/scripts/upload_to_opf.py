#!/usr/bin/env python3
"""Upload French textile products to Open Products Facts and Folksonomy Engine.

This script:
1. Downloads the source CSV from data.gouv.fr (if not already present)
2. Creates/updates products on Open Products Facts using the Python SDK
3. Uploads environmental cost properties to the Folksonomy Engine REST API

Authentication:
    - Username: ecobalyse-textile-import
    - Password: set via ECOBALYSE_TEXTILE_IMPORT environment variable

Usage:
    # Test run with 10 products (default)
    python3 upload_to_opf.py

    # Upload 100 products
    python3 upload_to_opf.py --limit 100

    # Upload all products
    python3 upload_to_opf.py --limit 0

    # Use a local source CSV
    python3 upload_to_opf.py --input path/to/source.csv
"""

import argparse
import csv
import hashlib
import os
import sys
import time
import urllib.request

import openfoodfacts
import requests

from field_mapping import (
    CATEGORY_MAP,
    DATA_SOURCE_URL,
    ECOBALYSE_BASE_URL,
    FOLKSONOMY_FIELD_MAP,
)

# Account for uploading
USERNAME = "ecobalyse-textile-import"
PASSWORD_ENV_VAR = "ECOBALYSE_TEXTILE_IMPORT"

# User agent for API requests
USER_AGENT = "ecobalyse-textile-import/1.0 (Open Products Facts data import)"

# Folksonomy Engine API base URL
FOLKSONOMY_API_URL = "https://api.folksonomy.openfoodfacts.org"

# Delay between API calls to avoid rate limiting (seconds)
API_DELAY = 0.5

# Folksonomy keys to upload (exclude non-environmental fields)
FOLKSONOMY_KEYS = [
    k for k in FOLKSONOMY_FIELD_MAP.values()
    if k.startswith("textile:french_environmental_cost:")
]


def download_source(output_path):
    """Download the source CSV from data.gouv.fr."""
    print(f"Downloading data from {DATA_SOURCE_URL}...")
    urllib.request.urlretrieve(DATA_SOURCE_URL, output_path)
    print(f"Downloaded to {output_path}")


def get_password():
    """Get the password from environment variable."""
    password = os.environ.get(PASSWORD_ENV_VAR)
    if not password:
        print(
            f"Error: {PASSWORD_ENV_VAR} environment variable is not set.",
            file=sys.stderr,
        )
        sys.exit(1)
    return password


def build_labels(row):
    """Build labels string from score and durability values."""
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
    return CATEGORY_MAP.get(french_category, french_category)


def get_product_code(row):
    """Get or generate a product barcode."""
    gtin = row.get("GTIN", "").strip()
    if gtin:
        return gtin
    brand = row.get("Marque", "").strip()
    ref = row.get("Référence interne", "").strip()
    cat = row.get("Catégorie", "").strip()
    key = f"{brand}|{ref}|{cat}"
    short_hash = hashlib.sha256(key.encode()).hexdigest()[:12]
    return f"textile_{short_hash}"


def authenticate_folksonomy(username, password):
    """Authenticate with the Folksonomy Engine and return a bearer token."""
    resp = requests.post(
        f"{FOLKSONOMY_API_URL}/auth",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    token_data = resp.json()
    return token_data["access_token"]


def upload_folksonomy_tag(token, product_code, key, value):
    """Upload a single key/value tag to the Folksonomy Engine.

    First tries to create (POST). If the tag already exists (409 conflict),
    fetches the current version and updates (PUT) instead.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {
        "product": product_code,
        "k": key,
        "v": str(value),
        "version": 1,
    }

    # Try to create the tag
    resp = requests.post(
        f"{FOLKSONOMY_API_URL}/product",
        json=body,
        headers=headers,
        timeout=30,
    )

    if resp.status_code == 409:
        # Tag already exists — fetch current version and update
        get_resp = requests.get(
            f"{FOLKSONOMY_API_URL}/product/{product_code}/{key}",
            headers=headers,
            timeout=30,
        )
        if get_resp.status_code == 200:
            existing = get_resp.json()
            current_version = existing.get("version", 1)
            body["version"] = current_version + 1
            resp = requests.put(
                f"{FOLKSONOMY_API_URL}/product",
                json=body,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
        else:
            get_resp.raise_for_status()
    elif resp.status_code >= 400:
        resp.raise_for_status()


def upload_product(api, row, folksonomy_token, dry_run=False):
    """Upload a single product to OPF and its properties to Folksonomy Engine.

    Returns (success_opf, success_folksonomy, code).
    """
    code = get_product_code(row)
    french_category = row.get("Catégorie", "").strip()

    # Build the OPF product body
    opf_body = {
        "code": code,
        "product_name_fr": row.get("Référence interne", "").strip(),
        "brands": row.get("Marque", "").strip(),
        "categories": map_category(french_category),
        "labels": build_labels(row),
    }

    # Step 1: Upload to Open Products Facts
    opf_success = False
    if dry_run:
        print(f"  [DRY RUN] Would upload to OPF: {code}")
        opf_success = True
    else:
        try:
            api.product.update(opf_body)
            opf_success = True
        except Exception as e:
            print(f"  Error uploading {code} to OPF: {e}", file=sys.stderr)

    # Step 2: Upload folksonomy properties
    folk_success = False
    if dry_run:
        print(f"  [DRY RUN] Would upload {len(FOLKSONOMY_KEYS)} folksonomy tags for {code}")
        folk_success = True
    elif opf_success and folksonomy_token:
        try:
            # Build a reverse mapping: folksonomy key -> original French column
            reverse_map = {v: k for k, v in FOLKSONOMY_FIELD_MAP.items()}

            for folk_key in FOLKSONOMY_KEYS:
                orig_col = reverse_map.get(folk_key, "")
                value = row.get(orig_col, "").strip()
                if value:
                    upload_folksonomy_tag(folksonomy_token, code, folk_key, value)
                    time.sleep(0.1)  # Small delay between tags for same product

            folk_success = True
        except Exception as e:
            print(
                f"  Error uploading folksonomy tags for {code}: {e}",
                file=sys.stderr,
            )

    return opf_success, folk_success, code


def main():
    parser = argparse.ArgumentParser(
        description="Upload French textile products to OPF and Folksonomy Engine"
    )
    parser.add_argument(
        "--input",
        help="Path to source CSV (will download if not provided)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max number of products to upload (0 for all, default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without actually uploading",
    )
    args = parser.parse_args()

    # Get password (unless dry run)
    password = None
    if not args.dry_run:
        password = get_password()

    # Resolve input path
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    if args.input:
        input_path = args.input
    else:
        input_path = os.path.join(data_dir, "source.csv")
        if not os.path.exists(input_path):
            download_source(input_path)

    # Initialize the OPF API client
    api = None
    if not args.dry_run:
        api = openfoodfacts.API(
            user_agent=USER_AGENT,
            username=USERNAME,
            password=password,
            country="world",
            flavor="opf",
            environment="org",
        )

    # Authenticate with Folksonomy Engine
    folksonomy_token = None
    if not args.dry_run:
        print("Authenticating with Folksonomy Engine...")
        try:
            folksonomy_token = authenticate_folksonomy(USERNAME, password)
            print("Folksonomy Engine authentication successful.")
        except Exception as e:
            print(
                f"Warning: Folksonomy Engine authentication failed: {e}",
                file=sys.stderr,
            )
            print(
                "Continuing with OPF upload only.",
                file=sys.stderr,
            )

    # Process and upload products
    print(f"\nReading source data from {input_path}...")
    limit_str = f" (limit: {args.limit})" if args.limit > 0 else " (all products)"
    print(f"Upload mode: {'DRY RUN' if args.dry_run else 'LIVE'}{limit_str}")
    print()

    opf_ok = 0
    folk_ok = 0
    errors = 0
    count = 0

    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if args.limit > 0 and count >= args.limit:
                break

            count += 1
            code = get_product_code(row)
            brand = row.get("Marque", "").strip()
            ref = row.get("Référence interne", "").strip()
            print(f"[{count}] {code} — {brand} — {ref}")

            opf_success, folk_success, _ = upload_product(
                api, row, folksonomy_token, dry_run=args.dry_run
            )

            if opf_success:
                opf_ok += 1
            else:
                errors += 1
            if folk_success:
                folk_ok += 1

            if not args.dry_run:
                time.sleep(API_DELAY)

    # Summary
    print(f"\n{'='*50}")
    print(f"Upload complete!")
    print(f"  Products processed: {count}")
    print(f"  OPF uploads successful: {opf_ok}")
    print(f"  Folksonomy uploads successful: {folk_ok}")
    print(f"  Errors: {errors}")


if __name__ == "__main__":
    main()
