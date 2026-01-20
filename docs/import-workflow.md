# Data Import Workflow

This document describes the complete workflow for importing external data into the Open Food Facts database.

## Overview

The data import process consists of several stages, from initial proposal to final integration. This ensures data quality, proper licensing, and community review.

## Workflow Stages

### 1. Discovery & Proposal 🔍

**Goal**: Identify potential data sources and propose imports to the community.

**Actions**:
- Identify a data source (producer, app, database, research institution)
- Verify data availability and licensing
- Assess data quality and scope
- Open an issue using the proposal template

**Checklist**:
- [ ] Data source identified and documented
- [ ] Contact established with data provider
- [ ] Licensing terms verified (must be open)
- [ ] Data scope and volume estimated
- [ ] Proposal issue created

**Timeline**: 1-7 days

---

### 2. Data Preparation 📊

**Goal**: Obtain, clean, and organize the data for import.

**Actions**:
- Obtain raw data from the source
- Clean and validate data
- Convert to standard formats (CSV/JSON)
- Organize files according to repository structure
- Create documentation (README, data dictionary)

**Checklist**:
- [ ] Raw data obtained
- [ ] Data cleaned and validated
- [ ] Duplicates removed
- [ ] Required fields present
- [ ] Data converted to standard format
- [ ] Directory structure created
- [ ] README documentation written
- [ ] License file added

**Timeline**: 1-14 days (varies by data size)

---

### 3. Quality Review 🔬

**Goal**: Ensure data quality and completeness before submission.

**Self-Review Checklist**:
- [ ] All required fields present
- [ ] Barcodes/GTINs validated
- [ ] Nutritional values reasonable
- [ ] Units standardized (metric)
- [ ] Countries use ISO codes
- [ ] Languages use ISO codes
- [ ] No personal/sensitive data
- [ ] File formats correct
- [ ] Documentation complete
- [ ] License compatible with ODbL

**Tools**:
- CSV validators
- Barcode checkers
- Data profiling tools
- Duplicate detection

**Timeline**: 2-5 days

---

### 4. Pull Request Submission 📤

**Goal**: Submit the import for community review.

**Actions**:
- Fork the repository
- Create a feature branch
- Add your import files
- Commit changes with clear messages
- Push to your fork
- Open a pull request

**PR Requirements**:
- Clear title describing the import
- Link to proposal issue
- Summary of data included
- Any special notes or considerations
- Checklist of completed requirements

**Template**:
```markdown
## Import: {Source Name}

Fixes #{proposal-issue-number}

### Summary
{Brief description of the import}

### Data Included
- {Number} products
- {Data types: nutritional, ingredients, images, etc.}
- {Geographic coverage}

### Checklist
- [ ] Proposal approved
- [ ] Data cleaned and validated
- [ ] Documentation complete
- [ ] License verified
- [ ] Tests pass (if applicable)

### Notes
{Any special considerations}
```

**Timeline**: 1 day

---

### 5. Community Review 👥

**Goal**: Community members and maintainers review the submission.

**Review Aspects**:
- **Data Quality**: Accuracy, completeness, consistency
- **Documentation**: Clear, thorough, well-organized
- **Licensing**: Properly licensed and attributed
- **Technical**: File formats, structure, standards compliance
- **Scope**: Appropriate for Open Food Facts

**Reviewer Checklist**:
- [ ] Data files present and accessible
- [ ] README documentation complete
- [ ] License appropriate and documented
- [ ] Data quality acceptable
- [ ] No duplicates with existing imports
- [ ] File formats correct
- [ ] Follows repository structure
- [ ] Source legitimate and verified

**Feedback Loop**:
- Reviewers leave comments on the PR
- Contributor addresses feedback
- Updates pushed to the same branch
- Review continues until approved

**Timeline**: 3-14 days (depends on complexity and responsiveness)

---

### 6. Approval & Merge ✅

**Goal**: Merge approved imports into the repository.

**Requirements for Merge**:
- At least one maintainer approval
- All review comments addressed
- No merge conflicts
- All checks passing (if applicable)

**Actions**:
- Maintainer performs final review
- PR merged to main branch
- Import added to the repository
- Contributor notified

**Timeline**: 1 day after approval

---

### 7. Integration Planning 🗓️

**Goal**: Plan integration of the data into Open Food Facts production database.

**Actions**:
- Assess integration complexity
- Schedule integration window
- Prepare data transformation scripts
- Plan matching and deduplication strategy
- Coordinate with Open Food Facts technical team

**Considerations**:
- **Volume**: Large imports may need batching
- **Matching**: How to match products (barcode, name, etc.)
- **Conflicts**: How to handle existing product data
- **Priority**: Which data takes precedence
- **Validation**: Post-integration checks

**Timeline**: 1-7 days (varies by complexity)

---

### 8. Database Integration 🔄

**Goal**: Import data into Open Food Facts production database.

**Process**:
- Run data transformation scripts
- Validate transformed data
- Match products with existing database
- Import new products
- Update existing products (if applicable)
- Verify integration success

**Validation Steps**:
- [ ] All products imported successfully
- [ ] Matching worked correctly
- [ ] No data corruption
- [ ] Product pages display correctly
- [ ] Search indexes updated
- [ ] No performance degradation

**Timeline**: 1-7 days (varies by volume)

---

### 9. Post-Integration 📈

**Goal**: Monitor integration and handle any issues.

**Actions**:
- Monitor for errors or issues
- Respond to user feedback
- Document any problems and solutions
- Update wiki and documentation
- Plan future updates (if applicable)

**Long-term Maintenance**:
- Schedule periodic updates
- Monitor data source for changes
- Maintain contact with data provider
- Update documentation as needed

**Timeline**: Ongoing

---

## Import Types & Considerations

### One-Time Imports

For static datasets that won't be updated:

- Focus on data quality and completeness
- Ensure thorough documentation
- No need for update mechanisms
- Historical reference preserved

### Recurring Imports

For regularly updated data sources:

- Establish update frequency
- Document update process
- Plan for incremental updates
- Consider automation
- Version control strategy

### Large-Scale Imports

For datasets with 10,000+ products:

- Split into manageable files
- Use efficient formats (CSV over JSON)
- Plan batched integration
- Consider database performance
- Coordinate with technical team

### Small/Pilot Imports

For testing or proof-of-concept:

- Start small to validate process
- Document learnings
- Plan scaling strategy
- Use as template for larger imports

---

## Troubleshooting

### Common Issues

**Issue**: Data format not recognized
- **Solution**: Use CSV with UTF-8 encoding, or JSON

**Issue**: Barcodes invalid
- **Solution**: Validate barcodes using check-digit algorithms

**Issue**: Merge conflicts
- **Solution**: Rebase your branch on latest main

**Issue**: License unclear
- **Solution**: Contact data provider for clarification

**Issue**: Duplicate products
- **Solution**: Use deduplication scripts before submission

**Issue**: Large file size
- **Solution**: Split into multiple files or compress

---

## Tools & Resources

### Validation Tools
- **CSV Validator**: Online CSV syntax checkers
- **Barcode Validator**: EAN/UPC check digit validators
- **JSON Validator**: JSON syntax and schema validators

### Data Processing
- **Python/Pandas**: Data cleaning and transformation
- **OpenRefine**: Interactive data cleaning
- **csvkit**: Command-line CSV tools

### Version Control
- **Git**: Version control system
- **GitHub Desktop**: GUI for Git (optional)
- **GitKraken**: Alternative Git GUI (optional)

---

## Best Practices

1. **Start Small**: Begin with a subset of data to validate the process
2. **Document Everything**: Clear documentation saves time later
3. **Communicate Early**: Ask questions before you get stuck
4. **Be Patient**: Reviews take time, especially for large imports
5. **Follow Standards**: Use established formats and conventions
6. **Test Thoroughly**: Validate data before submission
7. **Stay Responsive**: Respond to feedback promptly
8. **Think Long-term**: Consider future updates and maintenance

---

## Contact & Support

- **Questions**: Open an issue with `question` label
- **Help**: Ask in pull request comments
- **Slack**: Join [#data-quality](https://slack.openfoodfacts.org)
- **Forum**: [Data Import Forum](https://forum.openfoodfacts.org)

---

**This workflow ensures high-quality data imports that benefit the entire Open Food Facts community! 🌍**
