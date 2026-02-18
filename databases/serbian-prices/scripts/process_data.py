#!/usr/bin/env python3
"""
Process Serbian price data and generate output files for:
1. Open Food Facts (products with barcodes and names)
2. Open Prices (price points)

This script reads all downloaded CSV files, normalizes the data,
and creates two output files.
"""

import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime
import csv

# Directories
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Expected column mappings (Serbian to English)
COLUMN_MAPPINGS = {
    # Common variations in column names
    'Barkod proizvoda': 'barcode',
    'barkod proizvoda': 'barcode',
    'Barkod': 'barcode',
    'barkod': 'barcode',
    'EAN': 'barcode',
    'ean': 'barcode',
    
    'Naziv proizvoda': 'product_name',
    'naziv proizvoda': 'product_name',
    'Proizvod': 'product_name',
    'proizvod': 'product_name',
    
    'Robna marka': 'brand',
    'robna marka': 'brand',
    'Marka': 'brand',
    'marka': 'brand',
    'Brand': 'brand',
    
    'Redovna cena': 'price',
    'redovna cena': 'price',
    'Cena': 'price',
    'cena': 'price',
    'Price': 'price',
    
    'Snižena cena': 'price_discounted',
    'snižena cena': 'price_discounted',
    'Sniženacena': 'price_discounted',
    
    'Datum cenovnika': 'date',
    'datum cenovnika': 'date',
    'Datum': 'date',
    'datum': 'date',
    
    'Naziv trgovca - formata*': 'retailer',
    'naziv trgovca - formata*': 'retailer',
    'Naziv trgovca': 'retailer',
    'naziv trgovca': 'retailer',
    'Trgovac': 'retailer',
    'trgovac': 'retailer',
    
    'NAZIV KATEGORIJE': 'category',
    'Naziv kategorije': 'category',
    'naziv kategorije': 'category',
    'Kategorija': 'category',
    'kategorija': 'category',
    
    'Jedinica mere': 'unit',
    'jedinica mere': 'unit',
    
    'stopa PDV': 'vat_rate',
    'Stopa PDV': 'vat_rate',
}


def detect_delimiter(file_path):
    """Detect CSV delimiter."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        first_line = f.readline()
        # Common delimiters in order of likelihood
        for delim in [';', ',', '\t', '|']:
            if delim in first_line:
                return delim
    return ','


def normalize_columns(df):
    """Normalize column names using mappings."""
    renamed_cols = {}
    for col in df.columns:
        col_stripped = col.strip()
        if col_stripped in COLUMN_MAPPINGS:
            renamed_cols[col] = COLUMN_MAPPINGS[col_stripped]
    
    if renamed_cols:
        df = df.rename(columns=renamed_cols)
    
    return df


def clean_barcode(barcode):
    """Clean and validate barcode."""
    if pd.isna(barcode):
        return None
    
    barcode_str = str(barcode).strip()
    
    # Remove common prefixes/suffixes
    barcode_str = barcode_str.replace('EAN-', '').replace('EAN', '')
    
    # Remove non-numeric characters
    barcode_clean = ''.join(c for c in barcode_str if c.isdigit())
    
    # Valid EAN lengths: 8, 12, 13, 14
    if len(barcode_clean) in [8, 12, 13, 14]:
        return barcode_clean
    
    return None


def clean_price(price):
    """Clean price value."""
    if pd.isna(price):
        return None
    
    price_str = str(price).strip()
    
    # Replace comma with dot for decimal separator
    price_str = price_str.replace(',', '.')
    
    # Remove non-numeric characters except dot
    price_str = ''.join(c for c in price_str if c.isdigit() or c == '.')
    
    try:
        price_float = float(price_str)
        return price_float if price_float > 0 else None
    except (ValueError, TypeError):
        return None


def process_csv_file(file_path):
    """Process a single CSV file."""
    print(f"  Processing: {file_path.name}")
    
    try:
        # Detect delimiter
        delimiter = detect_delimiter(file_path)
        
        # Read CSV
        df = pd.read_csv(
            file_path,
            delimiter=delimiter,
            encoding='utf-8',
            low_memory=False,
            on_bad_lines='skip'
        )
        
        # Normalize column names
        df = normalize_columns(df)
        
        # Check for required columns
        required_cols = ['barcode', 'product_name', 'price']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"    WARNING: Missing columns: {missing_cols}")
            print(f"    Available columns: {list(df.columns)}")
            return None
        
        # Clean data
        df['barcode_clean'] = df['barcode'].apply(clean_barcode)
        df['price_clean'] = df['price'].apply(clean_price)
        
        # Use discounted price if available and valid
        if 'price_discounted' in df.columns:
            df['price_discounted_clean'] = df['price_discounted'].apply(clean_price)
            df['final_price'] = df.apply(
                lambda row: row['price_discounted_clean'] 
                if pd.notna(row.get('price_discounted_clean')) and row.get('price_discounted_clean', 0) > 0
                else row['price_clean'],
                axis=1
            )
        else:
            df['final_price'] = df['price_clean']
        
        # Filter valid rows
        df_valid = df[
            df['barcode_clean'].notna() &
            df['product_name'].notna() &
            df['final_price'].notna()
        ].copy()
        
        print(f"    Total rows: {len(df)}, Valid rows: {len(df_valid)}")
        
        return df_valid
        
    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def generate_off_products(all_data):
    """Generate Open Food Facts product CSV."""
    print("\nGenerating Open Food Facts product file...")
    
    # Select relevant columns for OFF
    off_columns = ['barcode_clean', 'product_name']
    
    # Add optional columns if available
    if 'brand' in all_data.columns:
        off_columns.append('brand')
    if 'category' in all_data.columns:
        off_columns.append('category')
    
    # Create OFF dataframe
    off_df = all_data[off_columns].copy()
    
    # Rename columns to OFF format
    off_df = off_df.rename(columns={
        'barcode_clean': 'code',
        'product_name': 'product_name',
        'brand': 'brands',
        'category': 'categories'
    })
    
    # Remove duplicates, keeping first occurrence
    off_df = off_df.drop_duplicates(subset=['code'], keep='first')
    
    # Sort by barcode
    off_df = off_df.sort_values('code')
    
    print(f"  Total unique products: {len(off_df)}")
    
    return off_df


def generate_open_prices(all_data):
    """Generate Open Prices CSV."""
    print("\nGenerating Open Prices file...")
    
    # Select relevant columns for Open Prices
    prices_columns = ['barcode_clean', 'product_name', 'final_price']
    
    # Add optional columns if available
    if 'retailer' in all_data.columns:
        prices_columns.append('retailer')
    if 'date' in all_data.columns:
        prices_columns.append('date')
    if 'unit' in all_data.columns:
        prices_columns.append('unit')
    
    # Create prices dataframe
    prices_df = all_data[prices_columns].copy()
    
    # Rename columns to Open Prices format
    rename_map = {
        'barcode_clean': 'product_code',
        'product_name': 'product_name',
        'final_price': 'price',
        'retailer': 'location_name',
        'date': 'date',
        'unit': 'price_per'
    }
    prices_df = prices_df.rename(columns={k: v for k, v in rename_map.items() if k in prices_df.columns})
    
    # Add currency
    prices_df['currency'] = 'RSD'  # Serbian Dinar
    
    # Sort by barcode and price
    prices_df = prices_df.sort_values(['product_code', 'price'])
    
    print(f"  Total price points: {len(prices_df)}")
    
    return prices_df


def main():
    print("Serbian Price Data Processor")
    print("=" * 50)
    
    # Check if raw data exists
    if not RAW_DIR.exists() or not list(RAW_DIR.glob("*.csv")):
        print(f"ERROR: No CSV files found in {RAW_DIR}")
        print("Please run harvest_data.py first.")
        return 1
    
    # Create processed directory
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process all CSV files
    csv_files = list(RAW_DIR.glob("*.csv"))
    print(f"\nFound {len(csv_files)} CSV files to process")
    
    all_dataframes = []
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"\n[{i}/{len(csv_files)}]")
        df = process_csv_file(csv_file)
        if df is not None and len(df) > 0:
            # Add source file info
            df['source_file'] = csv_file.name
            all_dataframes.append(df)
    
    if not all_dataframes:
        print("\nERROR: No valid data processed!")
        return 1
    
    # Concatenate all data
    print("\nCombining all data...")
    all_data = pd.concat(all_dataframes, ignore_index=True)
    print(f"Total records: {len(all_data)}")
    
    # Generate OFF products file
    off_df = generate_off_products(all_data)
    off_file = PROCESSED_DIR / "serbian_prices_off_products.csv"
    off_df.to_csv(off_file, index=False, encoding='utf-8')
    print(f"  Saved to: {off_file}")
    
    # Generate Open Prices file
    prices_df = generate_open_prices(all_data)
    prices_file = PROCESSED_DIR / "serbian_prices_open_prices.csv"
    prices_df.to_csv(prices_file, index=False, encoding='utf-8')
    print(f"  Saved to: {prices_file}")
    
    # Save statistics
    stats = {
        "process_date": datetime.now().isoformat(),
        "total_files_processed": len(all_dataframes),
        "total_records": len(all_data),
        "unique_products": len(off_df),
        "total_prices": len(prices_df),
        "unique_barcodes": all_data['barcode_clean'].nunique(),
        "unique_retailers": all_data['retailer'].nunique() if 'retailer' in all_data.columns else 0,
    }
    
    stats_file = PROCESSED_DIR / "processing_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistics saved to: {stats_file}")
    
    # Summary
    print("\n" + "=" * 50)
    print("PROCESSING SUMMARY")
    print("=" * 50)
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
