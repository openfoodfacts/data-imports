# Serbian Price Database Import

## Source Information

- **Organization**: Government of Serbia / Vlada Republike Srbije
- **Website**: https://data.gov.rs
- **Data Portal**: https://data.gov.rs/sr/datasets/?q=Cenovnici%20proizvoda%20po%20Uredbi%20o%20obaveznoj%20evidenciji%20i%20dostavljanju%20cena
- **License**: Public Domain
- **Regulation**: Serbian regulation on mandatory price records and submission (Uredba o obaveznoj evidenciji i dostavljanju cena)
- **Update Frequency**: Weekly (varies by retailer)
- **Export Date**: Automated - fetches latest data
- **Data Version**: Dynamic - updated regularly by retailers

## Data Description

This import contains price data from Serbian retailers submitted to the government in compliance with price transparency regulations. The data includes retail prices for consumer products with barcodes, product names, brands, and pricing information.

### Purpose

The Serbian government requires retailers to submit price lists to ensure market transparency and enable price monitoring. This data provides valuable information about:
- Product availability across different retailers
- Price variations between stores
- Regular and promotional pricing
- Product categorization and brands

### Coverage

- **Number of Products**: 100,000+ unique products (varies over time)
- **Product Categories**: Food, beverages, household items, personal care, etc.
- **Country**: Serbia (RS)
- **Languages**: Serbian (Cyrillic and Latin scripts)
- **Retailers**: 25+ major Serbian retail chains
- **Time Period**: Current price lists (updated weekly)

## Data Files

The import creates the following directory structure:

```
databases/serbian-prices/
├── README.md                              # This file
├── data/
│   ├── raw/                              # Downloaded CSV files from data.gov.rs
│   │   ├── {dataset_id}_{retailer}_{resource_id}.csv
│   │   └── harvest_metadata.json        # Download metadata
│   └── processed/                        # Processed output files
│       ├── serbian_prices_off_products.csv    # For Open Food Facts
│       ├── serbian_prices_open_prices.csv     # For Open Prices
│       └── processing_stats.json              # Processing statistics
└── scripts/
    ├── harvest_data.py                   # Download data from API
    ├── process_data.py                   # Process and generate outputs
    └── explore_data.py                   # Data exploration tool
```

## Data Schema

### Raw CSV Files (from data.gov.rs)

Raw CSV files from different retailers may have slightly different formats, but typically include:

| Field Name (Serbian) | Field Name (English) | Description | Type | Example |
|---------------------|---------------------|-------------|------|---------|
| KATEGORIJA | Category Code | Category identifier | String | "2" |
| NAZIV KATEGORIJE | Category Name | Product category | String | "Bezalkoholna pića, kafa, čaj" |
| Naziv proizvoda | Product Name | Product name | String | "Prolom voda NG Planinka 0,5l" |
| Robna marka | Brand | Brand name | String | "Prolom" |
| Barkod proizvoda | Product Barcode | EAN/UPC barcode | String | "8600169600046" |
| Jedinica mere | Unit of Measure | Unit (kom/kg/l/pak) | String | "kom" |
| Naziv trgovca - formata* | Retailer - Format | Retailer name and format | String | "Maxi" |
| Datum cenovnika | Price List Date | Date of price list | Date | "01-04-2025" |
| Redovna cena | Regular Price | Regular price | Number | "71.99" |
| Cena po jedinici mere | Price per Unit | Unit price | Number | "71.99" |
| Snižena cena | Discounted Price | Promotional price | Number | "" |
| Datum početka sniženja | Discount Start Date | Start of promotion | Date | "" |
| Datum kraja sniženja | Discount End Date | End of promotion | Date | "" |
| stopa PDV | VAT Rate | VAT percentage | Number | "20" |

### Open Food Facts Output (serbian_prices_off_products.csv)

Products file for importing into Open Food Facts:

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| code | Product barcode (EAN) | String | Yes | "8600169600046" |
| product_name | Product name | String | Yes | "Prolom voda NG Planinka 0,5l" |
| brands | Brand name | String | No | "Prolom" |
| categories | Product categories | String | No | "Beverages, Water" |

### Open Prices Output (serbian_prices_open_prices.csv)

Price points file for importing into Open Prices:

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| product_code | Product barcode | String | Yes | "8600169600046" |
| product_name | Product name | String | Yes | "Prolom voda NG Planinka 0,5l" |
| price | Price in RSD | Number | Yes | "71.99" |
| currency | Currency code | String | Yes | "RSD" |
| location_name | Retailer/store name | String | No | "Maxi" |
| date | Price list date | Date | No | "01-04-2025" |
| price_per | Unit of measure | String | No | "kom" |

## Data Quality Notes

### Known Issues

- **Location Information**: Most files only contain retailer chain names, not specific store locations. Location data is limited to national-level identifiers.
- **Format Variations**: Different retailers may format their CSV files differently (delimiter, encoding, column names).
- **Date Formats**: Date formats may vary between files (DD-MM-YYYY, DD/MM/YYYY, etc.).
- **Missing Barcodes**: Some products may have invalid or missing barcodes.
- **Encoding**: Files may use different character encodings (UTF-8, Windows-1250, ISO-8859-2) for Serbian Cyrillic/Latin text.

### Data Validation

The processing script performs the following validation:
- Barcode format validation (EAN-8, EAN-12, EAN-13, EAN-14)
- Price validation (positive numeric values)
- Removal of rows with missing critical fields
- Duplicate detection (same barcode from multiple retailers)
- Character encoding detection and normalization

### Missing Data

- **Location coordinates**: Not available in source data
- **Store addresses**: Not available in source data
- **Nutritional information**: Not available in source data
- **Product images**: Not available in source data
- **Product categories**: Available but not standardized

## Processing Notes

The data processing pipeline consists of:

1. **Harvesting** (`harvest_data.py`):
   - Queries the data.gov.rs API for all price datasets
   - Downloads all available CSV files
   - Saves files with unique identifiers
   - Records metadata about the download

2. **Processing** (`process_data.py`):
   - Detects CSV delimiters (`;`, `,`, `\t`, `|`)
   - Normalizes column names across different retailer formats
   - Cleans and validates barcodes
   - Cleans and validates prices
   - Uses discounted prices when available
   - Generates two output files:
     - `serbian_prices_off_products.csv` - Unique products for Open Food Facts
     - `serbian_prices_open_prices.csv` - All price points for Open Prices

3. **Deduplication**:
   - Products file: One row per unique barcode (first occurrence kept)
   - Prices file: All price points preserved (multiple retailers, dates)

## Usage

### Prerequisites

```bash
# Python 3.7+
pip install requests pandas beautifulsoup4 lxml
```

### Running the Import

```bash
# 1. Download data from data.gov.rs
cd databases/serbian-prices/scripts
python3 harvest_data.py

# 2. Process data and generate outputs
python3 process_data.py

# 3. (Optional) Explore data structure
python3 explore_data.py
```

### Automation

For periodic updates, you can set up a cron job:

```bash
# Run weekly (every Monday at 2 AM)
0 2 * * 1 cd /path/to/data-imports/databases/serbian-prices/scripts && python3 harvest_data.py && python3 process_data.py
```

## Integration Plan

### Open Food Facts

- **Matching Strategy**: Match by barcode (EAN/UPC)
- **Conflict Resolution**: Preserve existing detailed product data; add missing products
- **Priority**: Use as supplementary data source; existing verified data takes precedence
- **Fields to Import**:
  - `code`: Product barcode
  - `product_name`: Product name (Serbian)
  - `brands`: Brand name
  - `categories`: Product categories (if standardized)
- **Update Frequency**: Weekly

### Open Prices

- **Data Type**: All price points (not aggregated)
- **Location**: Serbia (country-level, with retailer names)
- **Currency**: Serbian Dinar (RSD)
- **Update Frequency**: Weekly
- **Notes**: Multiple price points per product from different retailers

## Update History

- **2025-02-10**: Initial import script created
  - Automated harvesting from data.gov.rs API
  - Processing for 27+ datasets from major Serbian retailers
  - Generated products file for Open Food Facts
  - Generated prices file for Open Prices

## License

The source data is published by the Government of Serbia under **Public Domain** license as part of the open data initiative (data.gov.rs).

According to Serbian regulations, this data is mandatorily submitted by retailers for public transparency and is freely available for use.

### Attribution

When using this data, attribution to the source is appreciated:

> "Data sourced from the Serbian Government Open Data Portal (data.gov.rs) - Price Lists submitted under Serbian price transparency regulations."

## Contact

For questions about this data import:

- **Repository**: https://github.com/openfoodfacts/data-imports
- **Issue Tracker**: https://github.com/openfoodfacts/data-imports/issues
- **Open Food Facts**: https://world.openfoodfacts.org
- **Open Prices**: https://prices.openfoodfacts.org

## Additional Resources

- **Data Portal**: https://data.gov.rs
- **API Documentation**: https://data.gov.rs/api/1/swagger.json
- **Serbian Price Regulation**: Government regulations on mandatory price reporting
- **Open Food Facts Import Guide**: https://wiki.openfoodfacts.org/Data_imports

---

**Thank you for contributing to Open Food Facts!** 🌍 🥫
