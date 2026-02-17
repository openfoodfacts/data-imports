# EU EPREL Database Import

## Source Information

- **Organization**: European Commission - EPREL (European Product Registry for Energy Labelling)
- **Website**: https://eprel.ec.europa.eu/
- **API Documentation**: https://eprel.ec.europa.eu/api/swagger-ui/index.html
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Data Version**: Ongoing (new products registered continuously)

## Data Description

This import contains product data from the EU EPREL database, which is the official European registry for energy labelling of products. The database contains technical specifications, energy efficiency data, and repairability information for electronics sold in the EU.

### Coverage

- **Product Categories**: Smartphones/Tablets, Televisions, Washing Machines, Refrigerators, Dishwashers, Air Conditioners, Lighting, and other energy-labelled product categories
- **Countries**: European Union member states
- **Languages**: Multilingual (product data as registered by manufacturers)
- **Time Period**: Ongoing since EPREL inception

### Key Data Points

For each product, EPREL provides:
- Supplier/Trademark and model identifier
- EPREL registration number (unique ID)
- Energy efficiency class
- Repairability class and index (for applicable categories)
- Technical specifications (battery, screen, durability, etc.)
- Market availability dates
- Repair and spare parts information

## Data Schema

### EPREL to Open Products Facts Field Mapping

The import script maps EPREL API field names to Open Products Facts (OPF) naming conventions.
Use `--format csv` to output with OPF field names.

#### Smartphones/Tablets

| EPREL API Field | OPF Field Name | Description | Example |
|-----------------|---------------|-------------|---------|
| supplierOrTrademark | brands | Manufacturer/brand | "Samsung" |
| modelIdentifier | manufacturer:reference_number | Model number | "SM-S928B" |
| eprelRegistrationNumber | eprel_id | Unique EPREL ID | 2372864 |
| gtin / ean / barcode | code | Product barcode (when available) | "5449000000996" |
| supplierName | supplier:name | Supplier legal name | "Samsung Electronics" |
| supplierAddress | supplier:address | Supplier postal address | "..." |
| supplierContact | supplier:contact | Supplier contact info | "..." |
| supplierEmail | supplier:email | Supplier email | "info@example.com" |
| supplierPhone | supplier:phone | Supplier phone | "+32..." |
| supplierWebsite | supplier:website | Supplier website | "https://..." |
| contactAddress | supplier:contact_address | Contact address | "..." |
| tradeMark | supplier:trademark | Registered trademark | "Galaxy" |
| dealerName | dealer:name | Dealer name | "..." |
| dealerAddress | dealer:address | Dealer address | "..." |
| energyClass | energy_efficiency_class:eu | EU energy rating | "A" |
| repairabilityClass | repairability_class:eu | EU repairability rating | "B" |
| repairabilityIndex | repairability_index:eu | Repairability score | 3.47 |
| onMarketStartDate | release_date | Market availability date | "2025-01-15" |
| guaranteeDuration | guarantee_duration:months | Warranty in months | 24 |
| minYearsSoftwareUpdates | consumer_electronics:min_years_software_updates | Years of OS updates | 5 |
| ratedBatteryCapacity | consumer_electronics:battery_capacity:mah | Battery capacity | 5000 |
| batteryEndurancePerCycle | battery_autonomy_per_cycle:eu:hours_min | Battery endurance/cycle | 3343 |
| batteryEnduranceInCycles | battery_endurance_in_cycles:eu | Endurance cycles | 8 |
| batteryCyclesFromPDF | battery_lifespan_in_cycles:eu:higher_or_equal_to | Rated battery cycles | 800 |
| batteryUserReplaceable | consumer_electronics:battery_user_replaceable | User-replaceable battery | True |
| chargerRequiredOutputPower | consumer_electronics:charger_output_power:w | Charger wattage | 33 |
| chargerReceptacleType | consumer_electronics:charger_receptacle_type | Charging port type | "USB_C" |
| operatingSystem | consumer_electronics:initial_operating_system | Device OS | "ANDROID" |
| isFoldable | consumer_electronics:is_foldable | Foldable device flag | False |
| ingressProtectionRating | ingress_protection_rating:ip | IP rating string | "IP68" |
| *(auto-generated)* | ingress_protection_rating:ip:number | IP rating number | 68 |
| ingressProtectionRatingSolid | ingress_protection_rating:ip:solid | Solid particle protection | "DUST_TIGHT" |
| ingressProtectionRatingWater | ingress_protection_rating:ip:water | Water protection | "CONT_IMMERSION" |
| immersionDepthWater | ingress_protection_rating:ip:immersion_depth:m | Immersion depth (m) | 1.5 |
| screenScratchResistance | consumer_electronics:screen_scratch_resistance:mohs | Screen Mohs hardness | "MOHS_7" |
| repeatedFreeFallReliabilityClass | repeated_free_fall_reliability_class:eu | EU drop test class | "A" |
| fallsWithoutDefect | consumer_electronics:falls_without_defect | Falls survived | 270 |
| disassemblyDepthScore | repairability_score:eu:disassembly_depth | Disassembly depth score | 4.05 |
| fastenersScore | repairability_score:eu:fasteners | Fasteners score | 5.0 |
| toolsScore | repairability_score:eu:tools | Tools required score | 4.0 |
| sparePartScore | repairability_score:eu:spare_parts | Spare parts score | "PRIORITY" |
| repairInfoScore | repairability_score:eu:repair_info | Repair info score | "NO_COST" |
| webLinkRepairInstructions | consumer_electronics:repair_instructions:url | Repair instructions URL | "https://..." |
| webLinkInfoSparePartsAvailability | consumer_electronics:spare_parts_info:url | Spare parts info URL | "https://..." |
| *(auto-generated)* | ec_energy_label:url | EPREL energy label page | "https://eprel.ec.europa.eu/..." |
| *(auto-generated)* | ec_energy_label:svg_url | Energy label SVG image | "https://eprel.ec.europa.eu/labels/.../Label_12345.svg" |

#### OPF Fields NOT Available from EPREL

The following OPF fields must come from other data sources:

`color`, `consumer_electronics:front_camera_resolution:mpx`, `consumer_electronics:initial_operating_system:version`,
`consumer_electronics:most_recent_network_generation`, `consumer_electronics:number_of_sim_slots:esim`,
`consumer_electronics:number_of_sim_slots:physical`, `consumer_electronics:ram_memory:capacity:gb`,
`consumer_electronics:rear_camera_resolution:mpx`, `consumer_electronics:rom_memory:capacity:gb`,
`consumer_electronics:screen_size:diagonal:inch`, `consumer_electronics:sd_card_max_capacity:gb`,
`consumer_electronics:sim_card_slot_type`, `consumer_electronics:nb_of_rear_cameras`,
`depth:mm`, `height:mm`, `weight:g`, `width:mm`,
`manufacturer:serie_reference`, `manufacturer:suggested_retail_price:eu:eur`

> **Note on barcodes/GTINs:** The EPREL API may occasionally include barcode/GTIN fields
> for some products. When present, these are mapped to the `code` field and used as the
> real barcode in the OFF import CSV. When no barcode is available (the common case),
> a placeholder `eprel_<id>` is used. Full barcode association requires the future
> Phase 2 endpoint (see Integration Plan below).

> **Note on supplier contacts:** Supplier/producer contact information (name, address,
> email, phone, website) is captured when returned by the EPREL API and mapped to
> `supplier:*` fields. Any EPREL fields not explicitly mapped are preserved with
> an `eprel:` prefix to avoid data loss.

## Files

- `scripts/eprel_client.py` - Python client for fetching data from the EPREL API (with rate limiting: 5 req/s)
- `scripts/field_mapping.py` - Field mapping from EPREL API names to OPF naming conventions
- `scripts/import_eprel.py` - Main ingestion script for downloading and storing EPREL data (JSON or CSV)
- `scripts/generate_off_csv.py` - Converts OPF-mapped EPREL CSV to OFF core import format (code, product_name, brands, categories, labels)
- `scripts/requirements.txt` - Python dependencies
- `scripts/tests/test_eprel_client.py` - Unit tests for API client
- `scripts/tests/test_field_mapping.py` - Unit tests for field mapping
- `scripts/tests/test_generate_off_csv.py` - Unit tests for OFF CSV generation
- `data/eprel_smartphones_sample.csv` - Sample EPREL data (10 smartphones) with OPF field names
- `data/eprel_smartphones_off_import.csv` - Same data converted to OFF core import format

## Usage

### Prerequisites

```bash
cd databases/eprel/scripts
pip install -r requirements.txt
```

### Fetching Product Data

```bash
# Fetch smartphones data as JSON (raw EPREL fields)
python import_eprel.py --category smartphones --output ../data/

# Fetch as CSV with OPF field names (ready for Open Products Facts import)
python import_eprel.py --category smartphones --format csv --fetch-details --output ../data/

# Fetch with a specific API key
python import_eprel.py --category smartphones --api-key YOUR_API_KEY --output ../data/

# Fetch multiple categories
python import_eprel.py --category smartphones --category televisions --output ../data/

# Fetch with pagination limits
python import_eprel.py --category smartphones --max-pages 5 --output ../data/

# Fetch and also download energy label SVGs
python import_eprel.py --category smartphones --format csv --fetch-details --download-labels --output ../data/
```

### Generating OFF Core Import CSV

After fetching EPREL data as CSV, generate a second CSV suitable for Open Food Facts core import:

```bash
# Convert OPF-mapped CSV to OFF core format
python generate_off_csv.py --input ../data/eprel_smartphones_sample.csv \
    --output ../data/eprel_smartphones_off_import.csv

# The OFF core CSV includes: code, product_name, brands, categories, labels,
# plus key technical fields (energy class, repairability, battery, etc.)
# Barcodes use format "eprel_<id>" since EPREL has no GTINs.
```

### GitHub Action (Sample Fetch)

A GitHub Action workflow is available to fetch sample data using the repository's EPREL API key:

1. Go to **Actions** → **EPREL Sample Fetch**
2. Click **Run workflow**
3. Select category, number of products, and output format
4. Download the generated sample from the workflow artifacts

### Running Tests

```bash
cd databases/eprel/scripts
python -m pytest tests/ -v
```

## Integration Plan

### Phase 1: Data Ingestion (Current)
- Fetch product data from the EPREL API
- Store raw data as JSON files in the `data/` directory
- Each product category stored in a separate file

### Phase 2: Barcode Association (Future)
- EPREL products are identified by EPREL ID (from QR code URLs like `https://eprel.ec.europa.eu/qr/[ID]`), not GTINs
- A future API endpoint will allow associating EPREL IDs with product barcodes (GTINs)
- Until association, products are stored in an `eprel_staging` collection

### Phase 3: Data Normalization (Future)
- Normalize EPREL data into the Open Products Facts schema
- Merge with existing product entries when barcodes match
- Handle conflicts between EPREL data and existing product data

## Notes

- The EPREL API requires an API key (stored as `EPREL_KEY` repository secret). Set via `--api-key` flag or `EPREL_API_KEY` env var.
- **Rate limit**: 5 requests per second (enforced automatically by the client).
- **Barcodes/GTINs**: The EPREL API does **not** provide product barcodes. Products are identified only by EPREL registration number. Barcode association requires the future Phase 2 endpoint.
- Data is licensed under CC BY 4.0, which is compatible with Open Food Facts (ODbL).
- The EPREL database is continuously updated as new products are registered.
- The API key must not be disclosed to third parties or used in frontend/client-side code (CORS restrictions apply).

## References

- [EPREL Portal](https://eprel.ec.europa.eu/)
- [EPREL API Swagger Documentation](https://eprel.ec.europa.eu/api/swagger-ui/index.html)
- [EPREL Smartphone Explorer (community tool)](https://eexntiso.github.io/eprel-smartphone-explorer/)
- [EU Energy Labelling Regulation](https://energy.ec.europa.eu/topics/energy-efficiency/energy-label-and-ecodesign_en)

## Update History

- **2026-02**: Initial import scripts and documentation

## License

Data from EPREL is available under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

> You are free to share and adapt the material for any purpose, even commercially,
> as long as you give appropriate credit.
> https://creativecommons.org/licenses/by/4.0/

### Attribution

When using this data, please attribute as: "Data from the European Product Registry for Energy Labelling (EPREL), European Commission"

## Contact

For questions about this data import, please open an issue in this repository.

---

**This import enables Open Products Facts to include EU energy labelling and repairability data for electronics.** ⚡📱
