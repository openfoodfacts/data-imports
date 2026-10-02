# Rappel Conso Import

## Source Information

- **Organization**: DGCCRF / DGAL / DGEC / DGPR (French Government)
- **Website**: https://rappelconso.gouv.fr/
- **Dataset**: https://www.data.gouv.fr/datasets/jeu-de-donnees-rappelconso-v2-rappels-de-produits
- **API**: https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/
- **License**: Licence Ouverte / Open Licence v2.0 (Etalab)
- **Update Frequency**: Continuous (daily)

## Data Description

[Rappel Conso](https://rappelconso.gouv.fr/) is the official French product recall portal, maintained by government agencies including the DGCCRF (consumer goods and food safety), DGAL (food), DGEC (energy), and DGPR (environmental risks). It publishes recall notices for unsafe or non-compliant products sold in France.

This import focuses on **food products** (`categorie_produit = "alimentation"`) that carry a GTIN (barcode). When a product is recalled but does not yet exist in Open Food Facts, this script creates a minimal product entry with only identification data — **not** the recall reason or risk information.

### Coverage

- **Product Categories**: Food products recalled in France (Alimentation)
- **Countries**: France
- **Languages**: French
- **GTIN Coverage**: GTINs were added to the dataset in November 2024. Older records may not have GTINs.
- **Time Period**: Ongoing since 2021

### Key Data Points

For each new food product identified, the import captures:

| Source Field | OFF Field | Description |
|---|---|---|
| `identification_produits[0]` | `code` | GTIN barcode (first element of the identification list) |
| `libelle` | `product_name` | Product title/label |
| `marque_produit` | `brands` | Brand name |
| `sous_categorie_produit` | `categories` | Product subcategory |
| *(constant)* | `countries` | "France" |
| *(constant)* | `source` | "Rappel Conso" |
| `id` | `rappelconso:fiche_id` | Recall notice numeric ID |
| `lien_vers_la_fiche_rappel` | `rappelconso:lien_fiche` | URL of the recall notice |

Recall-specific data (reason for recall, risk description, etc.) is **intentionally excluded** from the OFF import to keep product entries factual.

### GTIN Extraction

GTINs are embedded in the `identification_produits` field, which is a list with the structure:

```
[GTIN, lot_number, date_type, date_start, (date_end)]
```

For recalls covering multiple products, groups are separated by the `|` character (either as a standalone list element, or prepended to the next GTIN as `|GTIN`). The import script correctly extracts GTINs from all groups.

## Files

- `scripts/rappelconso_client.py` - Python client for the data.economie.gouv.fr API (with pagination and retry logic)
- `scripts/import_rappelconso.py` - Main daily import script: fetches recalls, checks OFF, writes new-products CSV
- `scripts/requirements.txt` - Python dependencies
- `scripts/tests/test_rappelconso_client.py` - Unit tests for the API client
- `scripts/tests/test_import_rappelconso.py` - Unit tests for the import logic
- `data/` - Output directory for generated CSV files (daily imports)

## Usage

### Prerequisites

```bash
cd databases/rappelconso/scripts
pip install -r requirements.txt
```

### Running the Daily Import

```bash
# Process recalls from the last day (default — use for daily cron)
python import_rappelconso.py --output ../data/

# Process recalls from the last 7 days
python import_rappelconso.py --days 7 --output ../data/

# Process recalls since a specific date
python import_rappelconso.py --since 2024-11-29 --output ../data/

# Skip the OFF existence check (output all food products with GTINs)
python import_rappelconso.py --no-off-check --output ../data/

# Enable verbose logging
python import_rappelconso.py --verbose --output ../data/
```

The script outputs a CSV file named `rappelconso_new_products_YYYY-MM-DD.csv` in the output directory.

### Output CSV Format

The generated CSV has the following columns:

| Column | Description |
|---|---|
| `code` | GTIN barcode |
| `product_name` | Product name |
| `brands` | Brand name |
| `categories` | Product category |
| `countries` | "France" |
| `source` | "Rappel Conso" |
| `rappelconso:fiche_id` | Recall notice ID |
| `rappelconso:lien_fiche` | URL of the recall notice |

### Running Tests

```bash
cd databases/rappelconso/scripts
python -m pytest tests/ -v
```

### GitHub Action (Daily Import)

A GitHub Action workflow runs automatically every day at 06:00 UTC:

1. Fetches recalls published in the last 24 hours
2. Checks Open Food Facts for each product GTIN
3. Creates a CSV of products not yet in OFF
4. Commits the CSV to the repository

The workflow can also be triggered manually from **Actions** → **Rappel Conso Daily Import**.

## Integration Plan

### Phase 1: Data Collection (Current)
- Fetch daily recall data from the Rappel Conso API
- Filter food products with GTINs
- Check Open Food Facts for existing products
- Output CSV of new products

### Phase 2: OFF Import
- Submit the daily CSV to Open Food Facts for import
- Products are created with minimal data (code, name, brand, category)

### Phase 3: Enrichment
- Use other data sources to enrich the minimal product entries
- Add nutritional data, ingredients, etc.

## Notes

- The Rappel Conso V2 dataset (`rappelconso-v2-gtin-espaces`) embeds GTINs in the `identification_produits` field. Each recall can cover multiple products; the import script extracts all GTINs from all groups in the field.
- GTINs appear in the `identification_produits` field. Records without GTINs (empty first element) are skipped.
- The script uses the public OFF API (`https://world.openfoodfacts.org/api/v2/product/{barcode}.json`) to check for product existence. No OFF credentials are required for this check.
- The import only covers `categorie_de_produit = "Alimentation"` (food products), as Rappel Conso also covers non-food items (toys, electronics, cosmetics, etc.) which are outside the scope of Open Food Facts.

## Update History

- **2026-02**: Initial import scripts and documentation

## License

Data from Rappel Conso is published under the **Licence Ouverte / Open Licence v2.0** by Etalab, which is compatible with Open Food Facts (ODbL).

> https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf

### Attribution

When using this data, please attribute as: "Données issues de RappelConso, DGCCRF/DGAL/DGEC/DGPR"

## References

- [Rappel Conso portal](https://rappelconso.gouv.fr/)
- [Dataset on data.gouv.fr](https://www.data.gouv.fr/datasets/jeu-de-donnees-rappelconso-v2-rappels-de-produits)
- [OpenDataSoft API documentation](https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/rappelconso-v2-gtin-espaces/)
- [Etalab Open Licence v2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence)
