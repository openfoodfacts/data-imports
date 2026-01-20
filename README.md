# Open Food Facts - Data Imports

[![Project Status](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/openfoodfacts/data-imports)
[![License](https://img.shields.io/badge/license-ODbL-blue.svg)](https://opendatacommons.org/licenses/odbl/)
[![Contributors](https://img.shields.io/github/contributors/openfoodfacts/data-imports.svg)](https://github.com/openfoodfacts/data-imports/graphs/contributors)

Welcome to the Open Food Facts Data Imports repository! 🌍 🥫 📊

This repository tracks and manages external data imports from various sources to enrich the [Open Food Facts](https://world.openfoodfacts.org/) database. We collect nutritional data, product information, and ingredient details from food producers, apps, labels, public databases, and research institutions.

## 📋 Table of Contents

- [About](#about)
- [Data Sources](#data-sources)
- [Repository Structure](#repository-structure)
- [How to Contribute](#how-to-contribute)
- [Import Process](#import-process)
- [Data Quality Guidelines](#data-quality-guidelines)
- [Examples](#examples)
- [Support](#support)
- [License](#license)

## 🎯 About

Open Food Facts is a free, open, collaborative database of food products from around the world. This repository serves as a centralized location to:

- **Track external data imports** from various partners and sources
- **Document data sources** including apps, labels, public databases, and research data
- **Maintain import history** and provenance information
- **Coordinate with food producers** who want to share their product data
- **Ensure data quality** through proper documentation and review processes

## 🗂️ Data Sources

We accept data from various sources:

### 1. **Food Producers & Manufacturers**
Direct product data from companies including:
- Nutritional values
- Ingredient lists
- Allergen information
- Product images and packaging details
- Certifications and labels

### 2. **Mobile Apps & Platforms**
Data from partner applications that collect food information:
- Shopping apps
- Nutrition tracking apps
- Recipe applications
- Retail platforms

### 3. **Public & Government Databases**
Official food databases from government agencies:
- USDA FoodData Central
- European food composition databases
- National nutrition databases
- Regulatory databases

### 4. **Research Institutions**
Academic and scientific data sources:
- University research projects
- Food science studies
- Nutrition research data
- Clinical trial information

### 5. **Label & Certification Bodies**
Information from certification organizations:
- Organic labels
- Fair trade certifications
- Quality marks
- Environmental certifications

## 📁 Repository Structure

```
data-imports/
├── README.md                          # This file
├── CONTRIBUTING.md                    # Contribution guidelines
├── producers/                         # Data from food producers
│   ├── {producer-name}/              # One directory per producer
│   │   ├── README.md                 # Import metadata & documentation
│   │   ├── data/                     # Raw data files
│   │   └── processed/                # Processed/cleaned data
├── apps/                              # Data from mobile apps & platforms
│   └── {app-name}/
├── databases/                         # Public & government databases
│   └── {database-name}/
├── research/                          # Research institution data
│   └── {institution-name}/
├── labels/                            # Label & certification data
│   └── {label-name}/
├── templates/                         # Templates for new imports
│   ├── import-template.md
│   └── data-format-examples/
└── docs/                              # Additional documentation
    ├── import-workflow.md
    ├── data-formats.md
    └── quality-guidelines.md
```

## 🤝 How to Contribute

We welcome contributions from everyone! Here's how you can help:

### For Data Contributors

1. **Check existing imports** - Review the repository to avoid duplicates
2. **Prepare your data** - Use our templates and follow quality guidelines
3. **Open an issue** - Describe your data source and import plan
4. **Submit a Pull Request** - Include:
   - Data files (CSV, JSON, Excel, etc.)
   - README with source documentation
   - License and usage information
   - Contact information

### For Code Contributors

- Improve documentation
- Create data processing scripts
- Enhance import workflows
- Review and validate imports

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🔄 Import Process

### Step 1: Proposal
- Open an issue describing the data source
- Include: source name, data type, volume, update frequency
- Discuss licensing and data quality

### Step 2: Preparation
- Organize data in the appropriate directory
- Document the data source and import details
- Ensure proper licensing and attribution

### Step 3: Review
- Community review of data quality and documentation
- Verification of source legitimacy
- Check for duplicates or conflicts

### Step 4: Import
- Merge the Pull Request
- Document the import in the wiki
- Schedule integration into Open Food Facts database

### Step 5: Maintenance
- Track updates to the data source
- Monitor data quality
- Update documentation as needed

## ✅ Data Quality Guidelines

To maintain high-quality data in Open Food Facts:

### Required Information
- **Source**: Clear identification of data origin
- **License**: Open license (ODbL compatible preferred)
- **Date**: When the data was collected/exported
- **Contact**: Person or organization responsible
- **Format**: Well-structured data (CSV, JSON, Excel)

### Data Standards
- Use standard field names (see [data-formats.md](docs/data-formats.md))
- Include product identifiers (barcodes, GTINs)
- Provide complete nutritional information when available
- Use metric units (grams, milliliters, etc.)
- Follow ISO standards for countries, languages

### Documentation Requirements
- README in each data directory
- Clear description of data scope and limitations
- Attribution and licensing information
- Contact information for questions
- Update history and changelog

## 📚 Examples

### Current Imports

- **[KFC Nutritional Values](KFCNutritionnalValues.xlsx)** - Nutritional data for KFC menu items

### Template Structure

For a new import, create:
```
producers/acme-foods/
├── README.md                  # Import documentation
├── data/
│   ├── products.csv          # Product catalog
│   ├── nutritional.csv       # Nutritional values
│   └── images/               # Product images
└── LICENSE                    # Data license
```

See [templates/](templates/) for examples and starter files.

## 💬 Support

- **General Questions**: Open an issue in this repository
- **Open Food Facts**: Visit [world.openfoodfacts.org](https://world.openfoodfacts.org)
- **Slack**: Join our [Slack workspace](https://slack.openfoodfacts.org)
- **Forum**: [Open Food Facts Forum](https://forum.openfoodfacts.org)
- **Wiki**: [Data Imports Wiki](https://wiki.openfoodfacts.org/Data_imports)

## 📄 License

The database contents are licensed under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/).

Individual datasets may have additional licenses - check each import's README for specific licensing terms.

---

## 🌟 Acknowledgments

Thank you to all contributors who help make Open Food Facts a comprehensive, open database of food products worldwide!

- Food producers sharing their data openly
- App developers providing product information
- Research institutions contributing scientific data
- Community members reviewing and improving imports
- Everyone who adds products to Open Food Facts

**Together, we're making food transparency a reality! 🥗**
