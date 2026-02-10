#!/usr/bin/env python3
"""
Harvest Serbian price data from data.gov.rs API.

This script:
1. Fetches all datasets matching the Serbian price regulation
2. Downloads all CSV files
3. Saves them to the data directory
"""

import requests
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import time

# API configuration
API_BASE_URL = "https://data.gov.rs/api/1"
SEARCH_QUERY = "cenovnici"
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"


def fetch_all_datasets(query=SEARCH_QUERY, page_size=50):
    """Fetch all datasets from the API."""
    url = f"{API_BASE_URL}/datasets/"
    params = {
        "q": query,
        "page_size": page_size,
        "page": 1
    }
    
    all_datasets = []
    
    while True:
        print(f"Fetching page {params['page']}...")
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            datasets = data.get("data", [])
            if not datasets:
                break
            
            all_datasets.extend(datasets)
            
            # Check if there are more pages
            if len(all_datasets) >= data.get("total", 0):
                break
            
            params["page"] += 1
            time.sleep(0.5)  # Be polite to the server
            
        except Exception as e:
            print(f"Error fetching datasets: {e}")
            break
    
    print(f"Found {len(all_datasets)} datasets")
    return all_datasets


def download_csv_resources(datasets):
    """Download all CSV resources from datasets."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    downloaded = []
    errors = []
    
    for i, dataset in enumerate(datasets, 1):
        dataset_title = dataset.get("title", "Unknown")
        org_name = dataset.get("organization", {}).get("name", "Unknown")
        dataset_id = dataset.get("id", "unknown")
        
        print(f"\n[{i}/{len(datasets)}] Processing: {dataset_title}")
        print(f"  Organization: {org_name}")
        
        resources = dataset.get("resources", [])
        csv_resources = [r for r in resources if r.get("format", "").lower() == "csv"]
        
        if not csv_resources:
            print(f"  No CSV resources found")
            continue
        
        for j, resource in enumerate(csv_resources, 1):
            resource_url = resource.get("url")
            resource_title = resource.get("title", f"resource_{j}.csv")
            resource_id = resource.get("id", f"unknown_{j}")
            
            if not resource_url:
                print(f"  No URL for resource: {resource_title}")
                continue
            
            # Create safe filename
            safe_org_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in org_name)
            safe_org_name = safe_org_name.replace(' ', '_')[:50]
            filename = f"{dataset_id}_{safe_org_name}_{resource_id}.csv"
            filepath = DATA_DIR / filename
            
            print(f"  Downloading: {resource_title}")
            print(f"    URL: {resource_url}")
            print(f"    Saving to: {filename}")
            
            try:
                response = requests.get(resource_url, timeout=120, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = filepath.stat().st_size / (1024 * 1024)  # MB
                print(f"    Downloaded: {file_size:.2f} MB")
                
                downloaded.append({
                    "dataset_id": dataset_id,
                    "dataset_title": dataset_title,
                    "organization": org_name,
                    "resource_title": resource_title,
                    "resource_id": resource_id,
                    "filename": filename,
                    "url": resource_url,
                    "size_mb": file_size,
                    "download_time": datetime.now().isoformat()
                })
                
                time.sleep(1)  # Be polite to the server
                
            except Exception as e:
                error_msg = f"Error downloading {resource_title}: {e}"
                print(f"    ERROR: {error_msg}")
                errors.append({
                    "dataset_id": dataset_id,
                    "resource_id": resource_id,
                    "error": str(e),
                    "url": resource_url
                })
    
    return downloaded, errors


def save_metadata(downloaded, errors):
    """Save metadata about downloaded files."""
    metadata = {
        "harvest_date": datetime.now().isoformat(),
        "total_files": len(downloaded),
        "total_errors": len(errors),
        "files": downloaded,
        "errors": errors
    }
    
    metadata_file = DATA_DIR / "harvest_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\nMetadata saved to: {metadata_file}")
    return metadata


def main():
    print("Serbian Price Database Harvester")
    print("=" * 50)
    print(f"Data directory: {DATA_DIR}")
    print()
    
    # Fetch datasets
    datasets = fetch_all_datasets()
    
    if not datasets:
        print("No datasets found!")
        return 1
    
    # Download CSV files
    downloaded, errors = download_csv_resources(datasets)
    
    # Save metadata
    metadata = save_metadata(downloaded, errors)
    
    # Summary
    print("\n" + "=" * 50)
    print("HARVEST SUMMARY")
    print("=" * 50)
    print(f"Total datasets: {len(datasets)}")
    print(f"Files downloaded: {len(downloaded)}")
    print(f"Errors: {len(errors)}")
    
    if downloaded:
        total_size = sum(f['size_mb'] for f in downloaded)
        print(f"Total size: {total_size:.2f} MB")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error['resource_id']}: {error['error']}")
    
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
