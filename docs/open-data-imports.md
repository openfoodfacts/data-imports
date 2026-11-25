# Open Data Imports & Quality Checks

This guide covers how public/open datasets are discovered, prepared, and checked before going live on Open Food Facts.

## How an Import Usually Works

1. **Generate a CSV file** formatted for Open Food Facts (see [Data Formats](data-formats.md) for field names).
2. **Load it into the Producer Platform** under a bespoke organisation created for that dataset.
   > **Note:** Using a bespoke organisation on the Producer Platform currently poses issues with excessive data protection, so we may need to go another way for future imports.
3. **Check data quality on the platform.** Reviewing the imported products for missing fields, unit mismatches, bad barcodes, or formatting issues on the platform is critical **before** pushing anything to production.
4. **Push to production.**

## Help Wanted: Finish the USDA Import (80–90% Ready)

The USDA FoodData Central import is already **80–90% ready**. If you are interested in helping finish it, **the Open Food Facts team is willing to spend time mentoring you** through the remaining work and the quality checks.

Reach out on [Open Food Facts Slack](https://slack.openfoodfacts.org) or open an issue in this repository if you'd like to pick this up.

## Help Wanted: Hunting New Open Datasets

We are looking for volunteers to look for new open datasets—typically on **national open data portals**, government nutrition databases, or other public registries—and document them here.

You don't need to write import scripts to help with this. Opening an issue or adding a short `README.md` in `databases/` (or `research/` / `labels/`) with:
- A link to the dataset
- What kind of products/fields it covers (barcodes, nutrition, ingredients, etc.)
- Its license (e.g. CC BY, ODbL-compatible, public domain)

is already a huge help.
