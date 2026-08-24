#!/usr/bin/env python3
"""
Explore the Serbian government price database to understand the structure
and available datasets.
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_dataset_list():
    """Fetch the list of datasets from data.gov.rs"""
    base_url = "https://data.gov.rs/sr/datasets/"
    search_query = "?q=Cenovnici%20proizvoda%20po%20Uredbi%20o%20obaveznoj%20evidenciji%20i%20dostavljanju%20cena"
    
    url = base_url + search_query
    print(f"Fetching: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all dataset links
        datasets = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/datasets/r/' in href and 'cenovnici' in href.lower():
                dataset_info = {
                    'title': link.get_text(strip=True),
                    'url': href if href.startswith('http') else f"https://data.gov.rs{href}"
                }
                if dataset_info not in datasets:
                    datasets.append(dataset_info)
        
        print(f"\nFound {len(datasets)} datasets:")
        for i, ds in enumerate(datasets[:5], 1):
            print(f"{i}. {ds['title']}")
            print(f"   URL: {ds['url']}")
        
        return datasets
        
    except Exception as e:
        print(f"Error fetching datasets: {e}")
        return []

def explore_dataset(dataset_url):
    """Explore a specific dataset page to find CSV download links"""
    print(f"\nExploring dataset: {dataset_url}")
    
    try:
        response = requests.get(dataset_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find download links
        csv_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if href.endswith('.csv') or 'format=csv' in href.lower():
                csv_links.append({
                    'text': link.get_text(strip=True),
                    'url': href if href.startswith('http') else f"https://data.gov.rs{href}"
                })
        
        print(f"Found {len(csv_links)} CSV files")
        for i, link in enumerate(csv_links[:3], 1):
            print(f"  {i}. {link['text']}: {link['url']}")
        
        return csv_links
        
    except Exception as e:
        print(f"Error exploring dataset: {e}")
        return []

def sample_csv(csv_url, rows=5):
    """Download and sample a CSV file"""
    print(f"\nSampling CSV: {csv_url}")
    
    try:
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        
        # Try to detect encoding
        content = response.content
        
        # Try UTF-8 first
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try Windows-1250 (common for Serbian)
            try:
                text = content.decode('windows-1250')
            except UnicodeDecodeError:
                # Try ISO-8859-2
                text = content.decode('iso-8859-2', errors='replace')
        
        lines = text.split('\n')[:rows+1]
        print("Sample data:")
        for line in lines:
            print(line[:200] if len(line) > 200 else line)
        
        # Try to identify columns
        if lines:
            header = lines[0]
            columns = [col.strip() for col in header.split(',')]
            print(f"\nDetected columns ({len(columns)}):")
            for i, col in enumerate(columns[:20], 1):
                print(f"  {i}. {col}")
        
        return text
        
    except Exception as e:
        print(f"Error sampling CSV: {e}")
        return None

if __name__ == "__main__":
    print("Serbian Price Database Explorer")
    print("=" * 50)
    
    # Fetch dataset list
    datasets = fetch_dataset_list()
    
    # Explore first few datasets
    if datasets:
        print("\n\nExploring first dataset in detail...")
        csv_links = explore_dataset(datasets[0]['url'])
        
        # Sample first CSV
        if csv_links:
            sample_csv(csv_links[0]['url'])
