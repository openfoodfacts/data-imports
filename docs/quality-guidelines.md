# Data Quality Guidelines

Ensuring high-quality data imports is essential for Open Food Facts. This document provides guidelines for preparing and validating data before submission.

## Core Principles

1. **Accuracy**: Data should be correct and verifiable
2. **Completeness**: Include all available information
3. **Consistency**: Follow standard formats and conventions
4. **Transparency**: Document sources and methods clearly
5. **Openness**: Use open licenses compatible with ODbL

## Quality Checklist

Use this checklist before submitting an import:

### ✅ Data Source
- [ ] Source is legitimate and verifiable
- [ ] Source is properly documented
- [ ] Permission obtained to share data
- [ ] License is open and compatible
- [ ] Attribution requirements understood

### ✅ Data Structure
- [ ] Files use standard formats (CSV/JSON)
- [ ] UTF-8 encoding used
- [ ] Field names follow conventions
- [ ] One product per row/object
- [ ] No empty or malformed rows

### ✅ Product Identification
- [ ] Every product has a unique identifier
- [ ] Barcodes are valid (check digit)
- [ ] No duplicate products in dataset
- [ ] Identifiers match products correctly

### ✅ Basic Information
- [ ] Product names are clear and accurate
- [ ] Brand names included when available
- [ ] Quantities include units (g, ml, etc.)
- [ ] Categories are appropriate
- [ ] Countries use ISO codes

### ✅ Nutritional Data
- [ ] Values are per 100g or 100ml
- [ ] Units are metric (g, kJ, kcal)
- [ ] Values are within reasonable ranges
- [ ] No obvious errors or typos
- [ ] Energy values make sense

### ✅ Ingredients & Allergens
- [ ] Ingredient lists are complete
- [ ] Allergens clearly identified
- [ ] Text is readable and well-formatted
- [ ] Multiple languages separated

### ✅ Documentation
- [ ] README file included
- [ ] Data source documented
- [ ] Field descriptions provided
- [ ] Known limitations noted
- [ ] Contact information included

### ✅ Legal & Licensing
- [ ] License file included
- [ ] Attribution requirements met
- [ ] No copyright violations
- [ ] No personal data included
- [ ] Terms of use respected

## Data Validation

### Automated Validation

Before submission, validate your data:

#### Barcode Validation
```python
def validate_ean13(barcode):
    """Validate EAN-13 barcode check digit"""
    if len(barcode) != 13 or not barcode.isdigit():
        return False
    
    check_sum = 0
    for i, digit in enumerate(barcode[:12]):
        check_sum += int(digit) * (3 if i % 2 else 1)
    
    check_digit = (10 - (check_sum % 10)) % 10
    return check_digit == int(barcode[12])
```

#### CSV Structure Validation
```bash
# Check CSV structure
csvlint your-file.csv

# Validate encoding
file -bi your-file.csv  # Should show utf-8

# Check for duplicates
sort -u your-file.csv | wc -l  # Compare to original
```

#### Data Range Validation
```python
def validate_nutrition(row):
    """Check nutritional values are reasonable"""
    checks = {
        'energy_kcal': (0, 900),
        'fat_g': (0, 100),
        'carbohydrates_g': (0, 100),
        'proteins_g': (0, 100),
        'salt_g': (0, 50)
    }
    
    for field, (min_val, max_val) in checks.items():
        if field in row:
            value = float(row[field])
            if not min_val <= value <= max_val:
                return False, f"{field} out of range: {value}"
    
    return True, "OK"
```

### Manual Validation

#### Sample Review
- Review a random sample (50-100 products)
- Check for accuracy and completeness
- Verify data makes sense
- Look for patterns of errors

#### Cross-Reference
- Compare with existing Open Food Facts data
- Check product websites for accuracy
- Verify against official sources
- Validate nutritional values

#### Edge Case Testing
- Products with special characters
- Very long or short product names
- Products with many allergens
- International products

## Common Data Quality Issues

### Issue 1: Incorrect Units
**Problem**: Values not per 100g/100ml
```
❌ Bad:  energy_kcal: 150 (per serving)
✅ Good: energy_kcal: 500 (per 100g)
```

**Solution**: Convert all values to per 100g or per 100ml basis

### Issue 2: Invalid Barcodes
**Problem**: Barcodes with incorrect check digits
```
❌ Bad:  "301762042200X", "PROD-12345"
✅ Good: "3017620422003"
```

**Solution**: Validate all barcodes before submission

### Issue 3: Encoding Problems
**Problem**: Special characters display incorrectly
```
❌ Bad:  "CafÃ© au lait"
✅ Good: "Café au lait"
```

**Solution**: Save files in UTF-8 encoding

### Issue 4: Inconsistent Field Names
**Problem**: Mixed field naming
```
❌ Bad:  product_name, productName, Product_Name
✅ Good: product_name (consistent)
```

**Solution**: Use standard field names throughout

### Issue 5: Missing Required Data
**Problem**: Products without identifiers or names
```
❌ Bad:  barcode: "", product_name: ""
✅ Good: barcode: "3017620422003", product_name: "Nutella"
```

**Solution**: Ensure all products have required fields

### Issue 6: Unrealistic Values
**Problem**: Nutritional values that don't make sense
```
❌ Bad:  fat_g: 150 (per 100g impossible)
✅ Good: fat_g: 30.9
```

**Solution**: Validate ranges and sum of macronutrients

### Issue 7: Duplicate Products
**Problem**: Same product appears multiple times
```
❌ Bad:  3017620422003 appears in rows 10, 45, 103
✅ Good: Each barcode appears only once
```

**Solution**: Deduplicate before submission

### Issue 8: Poor Ingredient Lists
**Problem**: Unclear or incomplete ingredients
```
❌ Bad:  "sugar, oil, stuff"
✅ Good: "sugar, palm oil, hazelnuts (13%), ..."
```

**Solution**: Provide complete, well-formatted ingredient lists

## Quality Assurance Process

### Level 1: Self-Review
**Who**: Data contributor
**When**: Before submission
**Actions**:
- Run automated validation scripts
- Review sample of products manually
- Check documentation completeness
- Verify license and attribution

### Level 2: Community Review
**Who**: Community members
**When**: During PR review
**Actions**:
- Verify data quality
- Check documentation
- Test data integration
- Provide feedback

### Level 3: Maintainer Review
**Who**: Repository maintainers
**When**: Before merge
**Actions**:
- Final quality check
- License verification
- Integration planning
- Approval decision

### Level 4: Post-Import Review
**Who**: Open Food Facts community
**When**: After integration
**Actions**:
- Monitor product pages
- Check for errors
- User feedback
- Corrections as needed

## Data Completeness Levels

Different levels of data completeness:

### ⭐ Bronze - Basic
**Minimum requirements met**:
- Unique product identifier (barcode)
- Product name
- Basic documentation
- Open license

**Use case**: Initial import, placeholder data

### ⭐⭐ Silver - Standard
**Good quality data**:
- All Bronze requirements
- Brand, quantity, categories
- Countries where sold
- Nutritional information (basic)
- Ingredient list

**Use case**: Most imports should aim for this level

### ⭐⭐⭐ Gold - Comprehensive
**High quality, complete data**:
- All Silver requirements
- Complete nutritional information
- Detailed ingredient lists with percentages
- Allergen information
- Multiple languages
- Product images
- Labels and certifications

**Use case**: Premium imports from producers or detailed databases

### ⭐⭐⭐⭐ Platinum - Exceptional
**Outstanding quality and depth**:
- All Gold requirements
- Additional nutrients (vitamins, minerals)
- Multiple images (all angles)
- Packaging details
- Environmental/sustainability data
- Regular updates scheduled

**Use case**: Flagship imports from major partners

## Improving Data Quality

### For Existing Imports

If you have already submitted data and want to improve it:

1. **Open an enhancement issue**
2. **Describe the improvements**
3. **Submit a PR with updates**
4. **Reference original import**

### Iterative Improvement

Start with what you have, improve over time:
1. **Phase 1**: Basic data (Bronze/Silver)
2. **Phase 2**: Add missing fields
3. **Phase 3**: Enhance quality (Gold)
4. **Phase 4**: Add images, translations
5. **Phase 5**: Ongoing maintenance

## Tools & Resources

### Validation Tools

**Python**:
```python
# Install validation libraries
pip install pandas validators python-stdnum

# Example validation script
import pandas as pd
from stdnum import ean

# Load CSV
df = pd.read_csv('products.csv')

# Validate barcodes
df['valid_barcode'] = df['barcode'].apply(
    lambda x: ean.is_valid(str(x))
)

# Check for issues
invalid = df[~df['valid_barcode']]
print(f"Invalid barcodes: {len(invalid)}")
```

**Command Line**:
```bash
# Check CSV structure
csvlint data.csv

# Check encoding
file -bi data.csv

# Find duplicates
sort data.csv | uniq -d

# Count rows
wc -l data.csv
```

### Data Cleaning Tools

- **OpenRefine**: Interactive data cleaning and transformation
- **Pandas**: Python library for data manipulation
- **Excel**: Quick manual edits (save as CSV)
- **Google Sheets**: Collaborative editing
- **csvkit**: Command-line CSV tools

### Testing Your Import

Before submission, test with a small sample:

1. **Extract sample**: Take 10-50 products
2. **Create test import**: Use same structure
3. **Validate sample**: Run all checks
4. **Review manually**: Check each product
5. **Fix issues**: Apply fixes to full dataset
6. **Document**: Note any problems and solutions

## Documentation Quality

Good documentation is part of data quality:

### README Requirements
- **Clear source description**
- **Data scope and coverage**
- **File descriptions**
- **Field definitions**
- **Known limitations**
- **Contact information**
- **License details**

### Examples
Include examples of:
- Sample products
- Data format
- Special cases
- How to use the data

### Updates
Keep documentation current:
- Version numbers
- Change log
- Update history
- Known issues

## Red Flags

Watch out for these warning signs:

🚩 **Missing attribution or unclear source**
🚩 **Restrictive or unclear licensing**
🚩 **Many products with missing data**
🚩 **Nutritional values that don't add up**
🚩 **Suspiciously perfect or rounded numbers**
🚩 **Copy-paste errors across products**
🚩 **Mixed units or inconsistent formats**
🚩 **No documentation or minimal README**
🚩 **Unresponsive to review feedback**
🚩 **Personal or sensitive information included**

If you spot these issues, address them before submission.

## Getting Help

Need help improving your data quality?

- **Ask questions**: Open an issue
- **Request review**: Tag maintainers
- **Share samples**: For specific feedback
- **Join Slack**: Real-time discussion
- **Check docs**: Review examples and guides

## Summary

**Good data quality benefits everyone**:
- ✅ Accurate product information
- ✅ Better user experience
- ✅ Easier maintenance
- ✅ Trustworthy database
- ✅ Valuable for research
- ✅ Stronger partnerships

**Take the time to ensure quality**—it's worth it!

---

**Thank you for caring about data quality! 🌟**
