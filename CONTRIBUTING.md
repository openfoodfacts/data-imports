# Contributing to Open Food Facts Data Imports

Thank you for your interest in contributing to Open Food Facts! 🎉

This guide will help you contribute data imports to the Open Food Facts database.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Types of Contributions](#types-of-contributions)
- [Contribution Process](#contribution-process)
- [Data Requirements](#data-requirements)
- [Directory Structure](#directory-structure)
- [Best Practices](#best-practices)
- [Code of Conduct](#code-of-conduct)
- [Questions?](#questions)

## 🚀 Getting Started

### Prerequisites

1. **GitHub Account**: You'll need a GitHub account to contribute
2. **Data Source**: Have a legitimate source of food product data
3. **License**: Ensure your data can be shared under an open license
4. **Documentation**: Be prepared to document your data source

### First Steps

1. **Fork this repository** to your GitHub account
2. **Clone your fork** to your local machine
3. **Create a branch** for your contribution
4. **Read the guidelines** below carefully

## 🎯 Types of Contributions

We welcome several types of contributions:

### 1. Data Imports

The primary contribution type - adding new food product data:

- **Food Producer Data**: Nutritional information from manufacturers
- **App Data**: Product information collected by mobile applications
- **Database Exports**: Data from public or research databases
- **Label/Certification Data**: Information from certification bodies
- **Retail Data**: Product catalogs from stores or chains

### 2. Documentation Improvements

- Clarifying import guidelines
- Adding examples and templates
- Translating documentation
- Improving data format specifications

### 3. Code Contributions

- Data processing scripts
- Validation tools
- Import automation
- Quality checking utilities

### 4. Data Quality Reviews

- Reviewing proposed imports
- Verifying data accuracy
- Checking license compliance
- Testing data integrity

## 📝 Contribution Process

### Step 1: Propose Your Import

Before submitting data, **open an issue** with:

**Issue Title**: `[Import Proposal] {Source Name}`

**Issue Content**:
```markdown
## Data Source Information

- **Source Name**: 
- **Source Type**: [Producer/App/Database/Research/Label]
- **Description**: 
- **Number of Products**: 
- **Data Format**: [CSV/JSON/Excel/Other]
- **Update Frequency**: [One-time/Monthly/Quarterly/Yearly]
- **License**: 
- **Contact**: 

## Data Scope

- **Product Categories**: 
- **Geographical Coverage**: 
- **Languages**: 
- **Time Period**: 

## Additional Notes

[Any special considerations, limitations, or requirements]
```

### Step 2: Prepare Your Data

1. **Organize your files** according to the repository structure
2. **Clean your data**:
   - Remove duplicates
   - Standardize formats
   - Validate required fields
   - Check for errors

3. **Create documentation**:
   - Add a README.md in your import directory
   - Document data sources and methodology
   - Include license information
   - Provide contact details

### Step 3: Submit a Pull Request

1. **Create the appropriate directory structure**:
   ```
   producers/your-company/
   ├── README.md
   ├── data/
   │   └── your-data.csv
   └── LICENSE
   ```

2. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add [source name] data import"
   git push origin your-branch-name
   ```

3. **Open a Pull Request** with:
   - Clear title: `Add data import from {Source Name}`
   - Link to your proposal issue
   - Summary of what's included
   - Any special notes for reviewers

### Step 4: Review Process

- Community members will review your submission
- Maintainers may ask questions or request changes
- Address feedback and update your PR
- Once approved, your PR will be merged

### Step 5: Post-Merge

- Your data will be scheduled for integration into Open Food Facts
- You may be contacted for updates or clarifications
- Consider maintaining your import with periodic updates

## ✅ Data Requirements

### Mandatory Fields

Your data should include at minimum:

- **Product Identifiers**: Barcode (EAN/UPC), GTIN, or unique ID
- **Product Name**: In at least one language
- **Data Source**: Clear attribution
- **License**: Open license compatible with ODbL

### Recommended Fields

Include when available:

- **Nutritional Information**: Energy, fats, carbohydrates, proteins, salt, etc.
- **Ingredients**: Complete ingredient list
- **Allergens**: Allergen declarations
- **Categories**: Product categories/classifications
- **Brands**: Brand name(s)
- **Quantity**: Package size and unit
- **Countries**: Where the product is sold
- **Images**: Product photos (front, ingredients, nutrition facts)

### Data Formats

Accepted formats:

- **CSV** (preferred): UTF-8 encoding, comma-separated
- **JSON**: Structured, validated JSON
- **Excel**: .xlsx format, one product per row
- **TSV**: Tab-separated values
- **XML**: Well-formed with schema

### License Requirements

Data must be contributed under an open license:

- **ODbL** (Open Database License) - preferred
- **CC0** (Public Domain)
- **CC BY** (Attribution required)
- **CC BY-SA** (Attribution + ShareAlike)

⚠️ **Not Acceptable**: All Rights Reserved, Non-Commercial licenses (CC BY-NC), No-Derivatives licenses (CC BY-ND)

## 📁 Directory Structure

Place your data in the appropriate category:

### For Food Producers
```
producers/{company-name}/
├── README.md                  # Import documentation
├── data/
│   ├── products.csv          # Main product data
│   ├── nutritional.csv       # Nutritional information
│   ├── ingredients.csv       # Ingredient lists
│   └── images/               # Product images
├── processed/                 # Cleaned/processed data
└── LICENSE                    # Data license file
```

### For Mobile Apps
```
apps/{app-name}/
├── README.md
├── data/
│   └── export-{date}.json
└── LICENSE
```

### For Public Databases
```
databases/{database-name}/
├── README.md
├── data/
│   └── {database}-export.csv
├── scripts/                   # Processing scripts
│   └── transform.py
└── LICENSE
```

## 🌟 Best Practices

### Documentation

- **Be thorough**: Explain your data source, collection methods, and any limitations
- **Update regularly**: Keep documentation current as data changes
- **Provide examples**: Show sample records from your dataset
- **Include metadata**: Dates, versions, contact information

### Data Quality

- **Validate before submitting**: Check for errors, missing values, format issues
- **Use standard units**: Metric system (grams, milliliters, kilojoules)
- **Follow naming conventions**: Consistent field names, product names
- **Remove sensitive data**: No personal information, internal codes, or proprietary data

### File Management

- **Keep files manageable**: Split large datasets into multiple files
- **Use compression**: Zip or gzip large data files
- **Version your data**: Include dates or versions in filenames
- **Git-friendly formats**: Prefer CSV over binary formats when possible

### Communication

- **Be responsive**: Respond to questions and feedback promptly
- **Ask for help**: Don't hesitate to ask questions in issues
- **Collaborate**: Work with maintainers to improve your contribution
- **Share knowledge**: Document problems and solutions for others

## 📊 README Template for Imports

Each import should have a README.md with:

```markdown
# {Source Name} Import

## Source Information

- **Organization**: {Company/App/Database name}
- **Website**: {URL}
- **Contact**: {Email or contact person}
- **License**: {License type}
- **Date**: {Export or collection date}

## Data Description

{Brief description of what data is included}

### Coverage

- **Products**: {Number} products
- **Categories**: {Product types included}
- **Countries**: {Geographic coverage}
- **Languages**: {Available languages}

## Files

- `data/products.csv` - {Description}
- `data/nutritional.csv` - {Description}

## Data Fields

| Field Name | Description | Type | Example |
|------------|-------------|------|---------|
| barcode | Product EAN/UPC | String | "3017620422003" |
| name | Product name | String | "Nutella" |
| ... | ... | ... | ... |

## Notes

{Any important notes, limitations, or special considerations}

## Update History

- {Date}: Initial import
- {Date}: Updated with new products

## License

This data is licensed under {License Name}.
{License details or link}
```

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- **Be respectful**: Treat everyone with respect and courtesy
- **Be collaborative**: Work together to improve Open Food Facts
- **Be constructive**: Provide helpful feedback and suggestions
- **Be transparent**: Clearly document data sources and methods
- **Be patient**: Reviews and merges take time

## ❓ Questions?

- **General Questions**: Open an issue with the `question` label
- **Data-Specific**: Comment on your proposal issue
- **Technical Help**: Ask in the pull request
- **Community**: Join our [Slack](https://slack.openfoodfacts.org) or [Forum](https://forum.openfoodfacts.org)

---

**Thank you for contributing to Open Food Facts and helping make food transparency a reality! 🌍 🥫**
