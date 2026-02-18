# French Textile Environmental Cost Import

## Source Information

- **Organization**: Ministère de la Transition écologique (MTE)
- **Website**: https://affichage-environnemental.ecobalyse.beta.gouv.fr/
- **Contact**: affichage-environnemental@ecobalyse.beta.gouv.fr
- **License**: Licence Ouverte v2.0 (Etalab)
- **Data URL**: https://www.data.gouv.fr/datasets/affichage-environnemental-des-vetements
- **Export Date**: 2026-01-28

## Data Description

This dataset contains environmental cost scores for textile clothing products,
as declared by manufacturers under French regulation (Décret n° 2025-957).

Each product includes:
- Brand and internal reference
- GTIN barcode
- Overall environmental cost score (in impact points)
- Standardized environmental score (for comparison)
- Durability coefficient
- 18 detailed environmental impact categories (acidification, climate change, etc.)

### Coverage

- **Number of Products**: ~100,000 rows (~20,000 unique products)
- **Product Categories**: T-shirts, Jeans, Shirts, Pants, Sweaters, Dresses/Skirts, Coats/Jackets, Socks, Swimwear, Underwear
- **Countries**: France
- **Languages**: French
- **Brands**: ~50 brands

## Scripts

### generate_folksonomy_csv.py

Generates a CSV for import into the **Folksonomy Engine** with renamed columns
following the `textile:french_environmental_cost:*` naming convention.

```bash
cd databases/french_textile/scripts

# Download source data and generate folksonomy CSV
python3 generate_folksonomy_csv.py

# Or use a local source file
python3 generate_folksonomy_csv.py --input path/to/source.csv --output path/to/output.csv
```

### generate_off_csv.py

Generates a CSV for import into the **core of Open Products Facts** with fields:
- `code` — GTIN barcode
- `product_name_fr` — from "Référence interne"
- `brands` — from "Marque"
- `categories` — mapped to [OFF taxonomy](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/taxonomies/product/categories.txt)
- `labels` — "en:Score Environnemental {rounded score}", "en:Score de Durabilité {percentage}%"
- `url` — link to ecobalyse product page

```bash
cd databases/french_textile/scripts

# Download source data and generate OFF core CSV
python3 generate_off_csv.py

# Or use a local source file
python3 generate_off_csv.py --input path/to/source.csv --output path/to/output.csv
```

## Data Files

- `data/folksonomy_import_sample.csv` — Sample output (100 rows) of the Folksonomy Engine CSV
- `data/off_core_import_sample.csv` — Sample output (100 rows) of the OFF core import CSV

## Field Mapping

### Folksonomy Engine Fields

| Original French Column | Folksonomy Field Name |
|---|---|
| Marque | brands |
| Catégorie | textile:french_environmental_cost:category |
| GTIN | code |
| Référence interne | textile:french_environmental_cost:internal_reference |
| Score | textile:french_environmental_cost:score |
| Score standardisé | textile:french_environmental_cost:standardized_score |
| Durabilité | textile:french_environmental_cost:durability |
| Acidification | textile:french_environmental_cost:acidification |
| Changement climatique | textile:french_environmental_cost:climate_change |
| Écotoxicité de l'eau douce, corrigée | textile:french_environmental_cost:freshwater_ecotoxicity |
| Utilisation de ressources fossiles | textile:french_environmental_cost:fossil_resource_use |
| Eutrophisation eaux douces | textile:french_environmental_cost:freshwater_eutrophisation |
| Radiations ionisantes | textile:french_environmental_cost:ionizing_radiation |
| Utilisation des sols | textile:french_environmental_cost:land_use |
| Utilisation de ressources minérales et métalliques | textile:french_environmental_cost:mineral_and_metal_resource_use |
| Appauvrissement de la couche d'ozone | textile:french_environmental_cost:ozone_depletion |
| Formation d'ozone photochimique | textile:french_environmental_cost:photochemical_ozone_formation |
| Particules | textile:french_environmental_cost:particulate_matter |
| Eutrophisation marine | textile:french_environmental_cost:marine_eutrophisation |
| Eutrophisation terrestre | textile:french_environmental_cost:terrestrial_eutrophisation |
| Utilisation de ressources en eau | textile:french_environmental_cost:water_use |
| Complément microfibres | textile:french_environmental_cost:microfibers_complement |
| Complément export hors-Europe | textile:french_environmental_cost:non_europe_export_complement |
| Date de création | textile:french_environmental_cost:creation_date |

### Category Mapping

| French Category | OFF Taxonomy Category |
|---|---|
| T-shirt / Polo | en:T-shirts |
| Jean | en:Jeans |
| Chemise | en:Shirts & Tops |
| Chaussettes | en:Socks |
| Pantalon / Short | en:Pants |
| Pull | en:Pull-Over |
| Jupe / Robe | en:Dresses |
| Manteau / Veste | en:Coats & Jackets |
| Maillot de bain | en:Swimwear |
| Boxer / Slip (tricoté) | en:Boxer Briefs |
| Caleçon (tissé) | en:Underwear |

## Data Quality Notes

- Environmental scores are self-declared by manufacturers on a voluntary basis
- **We do not have the data to recompute these scores independently**
- The source data is updated monthly
- Some products may share the same "Référence interne" (internal reference) across different GTINs

## License

This data is licensed under the **Licence Ouverte v2.0** (Etalab Open License).

> https://www.etalab.gouv.fr/licence-ouverte-open-licence/

### Attribution

When using this data, please attribute as:
"Ministère de la Transition écologique — Affichage environnemental des vêtements"
