#!/usr/bin/env python3
"""
Test script to validate the Serbian price data import workflow.
This creates a minimal test dataset and validates the processing pipeline.
"""

import csv
import sys
from pathlib import Path
import subprocess

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def create_test_data():
    """Create a minimal test CSV file."""
    print("Creating test data...")
    
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    test_file = RAW_DIR / "test_data.csv"
    
    # Create test CSV with Serbian price data format
    test_data = [
        ["KATEGORIJA", "NAZIV KATEGORIJE", "Naziv proizvoda", "Robna marka", "Barkod proizvoda", 
         "Jedinica mere", "Naziv trgovca - formata*", "Datum cenovnika", "Redovna cena", 
         "Cena po jedinici mere", "Snižena cena", "Datum početka sniženja", "Datum kraja sniženja", "stopa PDV"],
        ["1", "Mlečni proizvodi", "Mleko 1L", "Imlek", "8600102000012", "kom", "Maxi", "01-02-2025", "120.99", "120.99", "", "", "", "20"],
        ["1", "Mlečni proizvodi", "Jogurt 150g", "Imlek", "8600102000029", "kom", "Maxi", "01-02-2025", "45.99", "45.99", "39.99", "01-02-2025", "07-02-2025", "20"],
        ["2", "Bezalkoholna pića", "Coca Cola 2L", "Coca Cola", "5449000000996", "kom", "Idea", "01-02-2025", "189.99", "189.99", "", "", "", "20"],
        ["3", "Higijena", "Pasta za zube", "Colgate", "8714789555492", "kom", "Mercator", "01-02-2025", "299.99", "299.99", "249.99", "01-02-2025", "14-02-2025", "20"],
    ]
    
    with open(test_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(test_data)
    
    print(f"  Created: {test_file}")
    print(f"  Rows: {len(test_data)}")
    return test_file


def run_processing():
    """Run the processing script."""
    print("\nRunning processing script...")
    
    process_script = SCRIPT_DIR / "process_data.py"
    result = subprocess.run(
        [sys.executable, str(process_script)],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print("ERROR:", result.stderr)
        return False
    
    return True


def validate_outputs():
    """Validate that output files were created correctly."""
    print("\nValidating outputs...")
    
    off_file = PROCESSED_DIR / "serbian_prices_off_products.csv"
    prices_file = PROCESSED_DIR / "serbian_prices_open_prices.csv"
    
    # Check files exist
    if not off_file.exists():
        print(f"  ERROR: {off_file} not found!")
        return False
    
    if not prices_file.exists():
        print(f"  ERROR: {prices_file} not found!")
        return False
    
    # Read and validate OFF products
    with open(off_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        off_products = list(reader)
    
    print(f"  OFF products: {len(off_products)} rows")
    
    if len(off_products) < 4:  # We have 4 products in test data
        print(f"  ERROR: Expected at least 4 products, got {len(off_products)}")
        return False
    
    # Validate required columns
    required_off_cols = ['code', 'product_name']
    if not all(col in off_products[0].keys() for col in required_off_cols):
        print(f"  ERROR: Missing required OFF columns")
        return False
    
    # Sample products
    print("  Sample OFF products:")
    for product in off_products[:3]:
        print(f"    - {product['code']}: {product['product_name']}")
    
    # Read and validate Open Prices
    with open(prices_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        prices = list(reader)
    
    print(f"\n  Open Prices: {len(prices)} rows")
    
    if len(prices) < 4:  # We have 4 products in test data
        print(f"  ERROR: Expected at least 4 price points, got {len(prices)}")
        return False
    
    # Validate required columns
    required_price_cols = ['product_code', 'price', 'currency']
    if not all(col in prices[0].keys() for col in required_price_cols):
        print(f"  ERROR: Missing required price columns")
        return False
    
    # Validate currency
    if not all(p['currency'] == 'RSD' for p in prices):
        print(f"  ERROR: Not all prices have RSD currency")
        return False
    
    # Sample prices
    print("  Sample prices:")
    for price in prices[:3]:
        print(f"    - {price['product_code']}: {price['price']} {price['currency']} @ {price.get('location_name', 'N/A')}")
    
    return True


def cleanup():
    """Clean up test files."""
    print("\nCleaning up test files...")
    
    test_file = RAW_DIR / "test_data.csv"
    if test_file.exists():
        test_file.unlink()
        print(f"  Removed: {test_file}")
    
    # Clean processed files
    for f in PROCESSED_DIR.glob("*"):
        if f.name != ".gitkeep":
            f.unlink()
            print(f"  Removed: {f}")


def main():
    print("Serbian Price Database - Test Script")
    print("=" * 50)
    
    try:
        # Create test data
        create_test_data()
        
        # Run processing
        if not run_processing():
            print("\nTEST FAILED: Processing error")
            return 1
        
        # Validate outputs
        if not validate_outputs():
            print("\nTEST FAILED: Validation error")
            return 1
        
        print("\n" + "=" * 50)
        print("TEST PASSED ✓")
        print("=" * 50)
        
        # Cleanup
        cleanup()
        
        return 0
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
