# {Source Name} Import Template

Use this template to document your data import. Replace the placeholder text with your information.

## Source Information

- **Organization**: {Company name, app name, or database name}
- **Website**: {Official website URL}
- **Contact Person**: {Name and title}
- **Contact Email**: {Email address}
- **License**: {Data license - e.g., ODbL, CC0, CC BY}
- **Export Date**: {When the data was exported - YYYY-MM-DD}
- **Data Version**: {Version number or identifier, if applicable}

## Data Description

{Provide a clear, concise description of the data being imported. Include:
- What type of products are covered
- What information is included (nutritional data, ingredients, images, etc.)
- Any unique characteristics or special features
- Known limitations or gaps}

### Coverage

- **Number of Products**: {Approximate count}
- **Product Categories**: {List main categories - e.g., beverages, snacks, dairy}
- **Countries**: {Geographic coverage - e.g., USA, France, Global}
- **Languages**: {Available languages for product information}
- **Brands**: {Number or list of brands included, if applicable}
- **Time Period**: {Data collection period}

## Data Files

List all files included in this import:

- `data/products.csv` - {Description of what this file contains}
- `data/nutritional.csv` - {Description of nutritional data}
- `data/ingredients.csv` - {Description of ingredient information}
- `data/images/` - {Description of image files}

## Data Schema

### Products File (products.csv)

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| barcode | Product EAN/UPC barcode | String | Yes | "3017620422003" |
| product_name | Product name | String | Yes | "Nutella" |
| brand | Brand name | String | No | "Ferrero" |
| quantity | Package size with unit | String | No | "400g" |
| categories | Product categories | String | No | "Spreads, Chocolate spreads" |
| countries | Countries where sold | String | No | "France, Germany, UK" |
| ... | ... | ... | ... | ... |

### Nutritional File (nutritional.csv)

| Field Name | Description | Type | Required | Example |
|------------|-------------|------|----------|---------|
| barcode | Product barcode (links to products) | String | Yes | "3017620422003" |
| energy_kj | Energy in kilojoules per 100g/ml | Number | No | 2252 |
| energy_kcal | Energy in kilocalories per 100g/ml | Number | No | 539 |
| fat_g | Fat in grams per 100g/ml | Number | No | 30.9 |
| saturated_fat_g | Saturated fat in grams per 100g/ml | Number | No | 10.6 |
| carbohydrates_g | Carbohydrates in grams per 100g/ml | Number | No | 57.5 |
| sugars_g | Sugars in grams per 100g/ml | Number | No | 56.3 |
| proteins_g | Proteins in grams per 100g/ml | Number | No | 6.3 |
| salt_g | Salt in grams per 100g/ml | Number | No | 0.107 |
| ... | ... | ... | ... | ... |

## Data Quality Notes

{Document any known data quality issues, limitations, or considerations:}

### Known Issues
- {Issue 1}
- {Issue 2}

### Data Validation
- {What validation was performed}
- {Any automated checks run}

### Missing Data
- {What fields commonly have missing values}
- {Why certain data might be incomplete}

## Processing Notes

{Document any processing, cleaning, or transformation done to the data:}

- {Step 1 - e.g., "Converted nutritional values to per 100g basis"}
- {Step 2 - e.g., "Standardized country codes to ISO 3166-1 alpha-2"}
- {Step 3 - e.g., "Removed products with incomplete barcodes"}

## Integration Plan

{Describe how this data should be integrated into Open Food Facts:}

- **Matching Strategy**: {How to match with existing products - e.g., by barcode}
- **Conflict Resolution**: {How to handle conflicts with existing data}
- **Priority**: {Whether this data should override existing values}
- **Update Frequency**: {How often updates will be provided}

## Update History

Track all updates to this import:

- **{YYYY-MM-DD}**: Initial import with {number} products
- **{YYYY-MM-DD}**: Updated with {number} new products, {number} products updated

## License

This data is licensed under **{License Name}**.

{Include the full license text or a link to it. For example:}

> This data is made available under the Open Database License (ODbL):
> http://opendatacommons.org/licenses/odbl/1.0/
> 
> Any rights in individual contents of the database are licensed under
> the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/

### Attribution

{If attribution is required, specify how it should be given:}

When using this data, please attribute as: "{Attribution text}"

## Contact

For questions about this data import:

- **Name**: {Contact person}
- **Email**: {Contact email}
- **Organization**: {Company/organization}
- **Alternative Contact**: {If applicable}

## Additional Resources

{Optional: Links to additional documentation, data dictionaries, API docs, etc.}

- {Link 1}
- {Link 2}

---

**Thank you for contributing to Open Food Facts!** 🌍 🥫
