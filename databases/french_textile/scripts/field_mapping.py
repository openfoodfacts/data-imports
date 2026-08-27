"""Field mappings for French textile environmental cost data.

Maps original French column names from the data.gouv.fr dataset
to folksonomy-style hierarchical field names for the Folksonomy Engine,
and maps textile categories to Open Products Facts taxonomy categories.
"""

# Mapping from original French column names to Folksonomy Engine field names
# Format: textile:french_environmental_cost:<english_name>
FOLKSONOMY_FIELD_MAP = {
    "Marque": "brands",
    "Catégorie": "textile:french_environmental_cost:category",
    "GTIN": "code",
    "Référence interne": "textile:french_environmental_cost:internal_reference",
    "Score": "textile:french_environmental_cost:score",
    "Score standardisé": "textile:french_environmental_cost:standardized_score",
    "Durabilité": "textile:french_environmental_cost:durability",
    "Acidification": "textile:french_environmental_cost:acidification",
    "Changement climatique": "textile:french_environmental_cost:climate_change",
    "Écotoxicité de l'eau douce, corrigée": "textile:french_environmental_cost:freshwater_ecotoxicity",
    "Utilisation de ressources fossiles": "textile:french_environmental_cost:fossil_resource_use",
    "Eutrophisation eaux douces": "textile:french_environmental_cost:freshwater_eutrophisation",
    "Radiations ionisantes": "textile:french_environmental_cost:ionizing_radiation",
    "Utilisation des sols": "textile:french_environmental_cost:land_use",
    "Utilisation de ressources minérales et métalliques": "textile:french_environmental_cost:mineral_and_metal_resource_use",
    "Appauvrissement de la couche d'ozone": "textile:french_environmental_cost:ozone_depletion",
    "Formation d'ozone photochimique": "textile:french_environmental_cost:photochemical_ozone_formation",
    "Particules": "textile:french_environmental_cost:particulate_matter",
    "Eutrophisation marine": "textile:french_environmental_cost:marine_eutrophisation",
    "Eutrophisation terrestre": "textile:french_environmental_cost:terrestrial_eutrophisation",
    "Utilisation de ressources en eau": "textile:french_environmental_cost:water_use",
    "Complément microfibres": "textile:french_environmental_cost:microfibers_complement",
    "Complément export hors-Europe": "textile:french_environmental_cost:non_europe_export_complement",
    "Date de création": "textile:french_environmental_cost:creation_date",
}

# Mapping from French textile categories to Open Products Facts taxonomy categories
# Based on https://github.com/openfoodfacts/openfoodfacts-server/blob/main/taxonomies/product/categories.txt
CATEGORY_MAP = {
    "T-shirt / Polo": "en:T-shirts",
    "Jean": "en:Jeans",
    "Chemise": "en:Shirts & Tops",
    "Chaussettes": "en:Socks",
    "Pantalon / Short": "en:Pants",
    "Pull": "en:Pull-Over",
    "Jupe / Robe": "en:Dresses",
    "Manteau / Veste": "en:Coats & Jackets",
    "Maillot de bain": "en:Swimwear",
    "Boxer / Slip (tricoté)": "en:Boxer Briefs",
    "Caleçon (tissé)": "en:Underwear",
}

# Base URL for constructing product links
ECOBALYSE_BASE_URL = (
    "https://affichage-environnemental.ecobalyse.beta.gouv.fr/marques/"
    "81ce375f-b59c-4934-b1d5-ba8a5697ae5e/"
)

# Source data URL
DATA_SOURCE_URL = (
    "https://static.data.gouv.fr/resources/"
    "affichage-environnemental-des-vetements/"
    "20260128-094517/products-done-2026-01-28t09-43-24.csv"
)
