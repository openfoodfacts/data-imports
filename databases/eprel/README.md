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

### Core Fields (common across product categories)

| Field Name | Description | Type | Example |
|------------|-------------|------|---------|
| eprelRegistrationNumber | Unique EPREL product ID | Integer | 2372864 |
| supplierOrTrademark | Manufacturer/brand name | String | "Samsung" |
| modelIdentifier | Model number/name | String | "SM-S928B" |
| deviceType | Product category | String | "SMARTPHONE" |
| energyClass | EU energy efficiency rating | String | "A" |
| onMarketStartDate | Market availability date | Date | "2025-01-15" |

### Smartphones/Tablets Additional Fields

| Field Name | Description | Type | Example |
|------------|-------------|------|---------|
| repairabilityClass | EU repairability rating | String | "B" |
| repairabilityIndex | Numeric repairability score | Float | 3.47 |
| guaranteeDuration | Warranty in months | Integer | 24 |
| minYearsSoftwareUpdates | Years of software support | Integer | 5 |
| ratedBatteryCapacity | Battery capacity in mAh | Integer | 5000 |
| batteryEndurancePerCycle | Battery endurance per cycle | Integer | 3343 |
| batteryEnduranceInCycles | Rated battery cycles | Integer | 8 |
| batteryCyclesFromPDF | Battery cycles from datasheet | Integer | 800 |
| batteryUserReplaceable | User-replaceable battery | Boolean | True |
| chargerRequiredOutputPower | Charger wattage | Integer | 33 |
| chargerReceptacleType | Charging port type | String | "USB_C" |
| operatingSystem | Device OS | String | "ANDROID" |
| isFoldable | Foldable device flag | Boolean | False |
| ingressProtectionRating | IP rating | String | "IP68" |
| screenScratchResistance | Mohs hardness rating | String | "MOHS_7" |

## Files

- `scripts/eprel_client.py` - Python client for fetching data from the EPREL API
- `scripts/import_eprel.py` - Main ingestion script for downloading and storing EPREL data
- `scripts/requirements.txt` - Python dependencies
- `scripts/tests/test_eprel_client.py` - Unit tests
- `data/` - Directory for downloaded EPREL data files (JSON/CSV)

## Usage

### Prerequisites

```bash
cd databases/eprel/scripts
pip install -r requirements.txt
```

### Fetching Product Data

```bash
# Fetch smartphones data (default category)
python import_eprel.py --category smartphones --output ../data/

# Fetch with a specific API key
python import_eprel.py --category smartphones --api-key YOUR_API_KEY --output ../data/

# Fetch multiple categories
python import_eprel.py --category smartphones --category televisions --output ../data/

# Fetch with pagination limits
python import_eprel.py --category smartphones --max-pages 5 --output ../data/
```

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

- The EPREL API may require an API key for access. Contact the EPREL team or check the API documentation.
- Data is licensed under CC BY 4.0, which is compatible with Open Food Facts (ODbL).
- The EPREL database is continuously updated as new products are registered.
- Rate limiting should be respected when fetching data from the API.

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
