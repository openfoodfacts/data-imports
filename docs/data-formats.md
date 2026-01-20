# Data Formats Specification

This document specifies the standard data formats for importing data into Open Food Facts.

## Overview

Open Food Facts accepts data in multiple formats, but standardized field names and formats ensure smooth integration. This guide covers:

- Standard file formats
- Required and optional fields
- Data types and validation rules
- Units and conventions
- Examples

## File Formats

### CSV (Recommended)

**Specifications**:
- **Encoding**: UTF-8 (required)
- **Delimiter**: Comma (`,`)
- **Quote Character**: Double quotes (`"`)
- **Line Ending**: Unix (`\n`) or Windows (`\r\n`)
- **Header Row**: Required (field names)

**Best Practices**:
- Use consistent field names
- Quote fields containing commas, newlines, or quotes
- Escape quotes with double quotes (`""`)
- Avoid empty lines
- One product per row

**Example**:
```csv
barcode,product_name,brand,quantity
"3017620422003","Nutella","Ferrero","400g"
"7622210449283","Oreo Original","Mondelez","154g"
```

### JSON

**Specifications**:
- Valid JSON syntax
- UTF-8 encoding
- Array of objects (one per product)
- Consistent property names

**Structure**:
```json
[
  {
    "barcode": "3017620422003",
    "product_name": "Nutella",
    "brand": "Ferrero",
    "quantity": "400g"
  },
  {
    "barcode": "7622210449283",
    "product_name": "Oreo Original",
    "brand": "Mondelez",
    "quantity": "154g"
  }
]
```

### Excel

**Specifications**:
- Format: `.xlsx` (not `.xls`)
- One product per row
- Header row with field names
- Single sheet preferred
- UTF-8 compatible

**Conversion**: Convert to CSV for version control

### TSV (Tab-Separated Values)

**Specifications**:
- UTF-8 encoding
- Tab delimiter (`\t`)
- Header row required
- Same rules as CSV

## Standard Field Names

### Product Identification

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| `barcode` | EAN, UPC, or other barcode | String | Yes* | "3017620422003" |
| `code` | Alternative to barcode | String | Yes* | "3017620422003" |
| `gtin` | Global Trade Item Number | String | No | "03017620422003" |
| `product_id` | Internal product ID | String | No | "PROD12345" |

*At least one identifier required

### Basic Information

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| `product_name` | Product name | String | Yes | "Nutella" |
| `generic_name` | Generic product description | String | No | "Chocolate hazelnut spread" |
| `brand` | Brand name(s) | String | No | "Ferrero" |
| `brands` | Alternative field name | String | No | "Ferrero" |
| `quantity` | Package size with unit | String | No | "400g" |
| `serving_size` | Serving size with unit | String | No | "15g" |

### Categories

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| `categories` | Product categories | String | No | "Spreads, Chocolate spreads" |
| `categories_en` | Categories in English | String | No | "Spreads, Chocolate spreads" |
| `main_category` | Primary category | String | No | "Spreads" |

**Format**: Comma or semicolon separated list

### Location

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| `countries` | Countries where sold | String | No | "France, Germany, UK" |
| `countries_en` | Countries (English names) | String | No | "France, Germany, United Kingdom" |
| `manufacturing_places` | Where manufactured | String | No | "France" |
| `origins` | Origin of ingredients | String | No | "European Union" |

**Format**: Use ISO 3166-1 alpha-2 codes when possible (e.g., "FR", "DE", "GB")

### Packaging

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| `packaging` | Packaging type(s) | String | No | "Glass jar, Metal lid" |
| `packaging_text` | Packaging instructions | String | No | "Recycle glass and metal" |

### Languages

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| `languages` | Available languages | String | No | "en, fr, de" |
| `lc` | Main language code | String | No | "en" |

**Format**: Use ISO 639-1 codes (e.g., "en", "fr", "de")

### Ingredients

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| `ingredients_text` | Full ingredient list | String | No | "Sugar, palm oil, hazelnuts (13%)..." |
| `ingredients_text_en` | Ingredients in English | String | No | "Sugar, palm oil, hazelnuts (13%)..." |
| `allergens` | Allergen declarations | String | No | "Milk, Nuts, Soybeans" |
| `traces` | May contain traces of | String | No | "Eggs, Peanuts" |

### Nutritional Information

All nutritional values should be **per 100g or 100ml**.

| Field Name | Description | Type | Unit | Example |
|------------|-------------|------|------|---------|
| `energy_kj` | Energy in kilojoules | Number | kJ | 2252 |
| `energy_kcal` | Energy in kilocalories | Number | kcal | 539 |
| `energy` | Energy (auto-detected) | Number | kJ or kcal | 2252 |
| `fat` | Total fat | Number | g | 30.9 |
| `fat_g` | Total fat (explicit) | Number | g | 30.9 |
| `saturated_fat` | Saturated fat | Number | g | 10.6 |
| `saturated_fat_g` | Saturated fat (explicit) | Number | g | 10.6 |
| `carbohydrates` | Total carbohydrates | Number | g | 57.5 |
| `carbohydrates_g` | Total carbs (explicit) | Number | g | 57.5 |
| `sugars` | Sugars | Number | g | 56.3 |
| `sugars_g` | Sugars (explicit) | Number | g | 56.3 |
| `fiber` | Dietary fiber | Number | g | 0 |
| `fiber_g` | Dietary fiber (explicit) | Number | g | 0 |
| `proteins` | Proteins | Number | g | 6.3 |
| `proteins_g` | Proteins (explicit) | Number | g | 6.3 |
| `salt` | Salt | Number | g | 0.107 |
| `salt_g` | Salt (explicit) | Number | g | 0.107 |
| `sodium` | Sodium | Number | g | 0.043 |
| `sodium_g` | Sodium (explicit) | Number | g | 0.043 |

**Note**: If you have sodium, calculate salt as: `salt = sodium × 2.5`

### Additional Nutrients

| Field Name | Description | Type | Unit |
|------------|-------------|------|------|
| `vitamin_a` | Vitamin A | Number | µg |
| `vitamin_c` | Vitamin C | Number | mg |
| `vitamin_d` | Vitamin D | Number | µg |
| `calcium` | Calcium | Number | mg |
| `iron` | Iron | Number | mg |
| `omega_3_fat` | Omega-3 fatty acids | Number | g |
| `cholesterol` | Cholesterol | Number | mg |

### Labels & Certifications

| Field Name | Description | Type | Example |
|------------|-------------|------|---------|
| `labels` | Certifications/labels | String | "Organic, Fair trade" |
| `labels_en` | Labels (English) | String | "Organic, Fair trade" |

### Images

| Field Name | Description | Type | Example |
|------------|-------------|------|---------|
| `image_url` | Product front image URL | String | "https://..." |
| `image_front_url` | Front image URL | String | "https://..." |
| `image_ingredients_url` | Ingredients image URL | String | "https://..." |
| `image_nutrition_url` | Nutrition facts image URL | String | "https://..." |
| `image_packaging_url` | Packaging image URL | String | "https://..." |

**Alternative**: Include image files in an `images/` directory with filenames like `{barcode}_front.jpg`

### Metadata

| Field Name | Description | Type | Example |
|------------|-------------|------|---------|
| `data_sources` | Data source identifier | String | "Producer import 2024" |
| `created_t` | Creation timestamp | Number | 1642521600 |
| `last_modified_t` | Last modified timestamp | Number | 1642608000 |
| `url` | Product URL | String | "https://..." |

## Data Types

### String
- Text values
- Use UTF-8 encoding
- Trim leading/trailing whitespace
- Empty strings for missing values or omit field

### Number
- Integer or decimal
- Use period (`.`) as decimal separator
- No thousands separators
- No units in the number field
- Empty or omit for missing values

### Boolean
- Use: `true`/`false`, `1`/`0`, or `yes`/`no`
- Consistent within a dataset

### Date/Timestamp
- ISO 8601 format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
- Unix timestamp (seconds since epoch)
- UTC timezone preferred

## Units & Conventions

### Weight/Volume
- **Metric system required**
- Weight: grams (g), kilograms (kg)
- Volume: milliliters (ml), liters (l)
- Include unit with value: "400g", "1L"

### Energy
- Kilojoules (kJ) preferred
- Kilocalories (kcal) also accepted
- Both can be provided

### Percentages
- Daily Value: as percentage (e.g., "15" for 15%)
- Composition: as percentage (e.g., "13" for 13% hazelnuts)

### Countries
- **ISO 3166-1 alpha-2** codes: FR, DE, GB, US
- English names: France, Germany, United Kingdom, United States
- Comma or semicolon separated for multiple

### Languages
- **ISO 639-1** codes: en, fr, de, es, it
- Comma separated for multiple

### Categories
- Use Open Food Facts taxonomy when possible
- Comma or semicolon separated
- From general to specific: "Snacks, Cookies, Chocolate cookies"

## Validation Rules

### Barcodes
- EAN-13: 13 digits, valid check digit
- EAN-8: 8 digits, valid check digit
- UPC-A: 12 digits, valid check digit
- UPC-E: 6 or 8 digits
- No spaces, dashes, or other characters

### Nutritional Values
- Must be ≥ 0
- Reasonable ranges:
  - Energy: 0-4000 kJ (0-900 kcal)
  - Fat: 0-100 g
  - Carbohydrates: 0-100 g
  - Proteins: 0-100 g
  - Salt: 0-50 g
- Sum of macronutrients should not exceed 100g (per 100g)

### Required Fields
At minimum, each product must have:
1. A unique identifier (barcode, code, or product_id)
2. A product name

## Multi-Language Support

### Language-Specific Fields

Add language suffix for multi-language data:
- `product_name_en`: "Chocolate spread"
- `product_name_fr`: "Pâte à tartiner"
- `product_name_de`: "Schokoladenaufstrich"
- `ingredients_text_en`: "Sugar, palm oil..."
- `ingredients_text_fr`: "Sucre, huile de palme..."

### Language Codes

Use ISO 639-1 two-letter codes:
- `en`: English
- `fr`: French
- `de`: German
- `es`: Spanish
- `it`: Italian
- `nl`: Dutch
- `pt`: Portuguese
- `ja`: Japanese
- `zh`: Chinese

## Complete Example

### CSV Format

```csv
barcode,product_name,brand,quantity,categories,countries,ingredients_text,allergens,energy_kj,energy_kcal,fat_g,saturated_fat_g,carbohydrates_g,sugars_g,proteins_g,salt_g
3017620422003,Nutella,Ferrero,400g,"Spreads, Chocolate spreads","FR, DE, GB","Sugar, palm oil, hazelnuts (13%), skimmed milk powder (8.7%), fat-reduced cocoa (7.4%), emulsifier: lecithins (soya), vanillin","Milk, Nuts, Soybeans",2252,539,30.9,10.6,57.5,56.3,6.3,0.107
```

### JSON Format

```json
{
  "barcode": "3017620422003",
  "product_name": "Nutella",
  "brand": "Ferrero",
  "quantity": "400g",
  "categories": "Spreads, Chocolate spreads",
  "countries": "FR, DE, GB",
  "ingredients_text": "Sugar, palm oil, hazelnuts (13%), skimmed milk powder (8.7%), fat-reduced cocoa (7.4%), emulsifier: lecithins (soya), vanillin",
  "allergens": "Milk, Nuts, Soybeans",
  "nutrition": {
    "energy_kj": 2252,
    "energy_kcal": 539,
    "fat_g": 30.9,
    "saturated_fat_g": 10.6,
    "carbohydrates_g": 57.5,
    "sugars_g": 56.3,
    "proteins_g": 6.3,
    "salt_g": 0.107
  }
}
```

## Common Issues & Solutions

### Issue: Special characters not displaying
**Solution**: Ensure UTF-8 encoding

### Issue: Commas breaking CSV
**Solution**: Quote fields containing commas

### Issue: Leading zeros in barcodes removed
**Solution**: Store barcodes as strings, not numbers

### Issue: Nutritional values not matching
**Solution**: Verify values are per 100g/100ml

### Issue: Countries not recognized
**Solution**: Use ISO 3166-1 alpha-2 codes

## Tools & Validators

### CSV Tools
- **csvlint**: CSV validator
- **CSVKit**: Command-line CSV utilities
- **Online CSV validators**

### JSON Tools
- **jsonlint**: JSON syntax validator
- **jq**: Command-line JSON processor

### Data Tools
- **OpenRefine**: Interactive data cleaning
- **Pandas**: Python data manipulation
- **Excel**: For quick edits (export to CSV)

## Questions?

If you have questions about data formats:
- Check the examples in `templates/data-format-examples/`
- Ask in an issue or pull request
- Join our [Slack](https://slack.openfoodfacts.org)

---

**Following these standards ensures smooth integration of your data into Open Food Facts! 📊**
