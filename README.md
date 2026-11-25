# Open Food Facts – Data Imports

This repository tracks external data imports for [Open Food Facts](https://world.openfoodfacts.org/) and its sister projects (Open Beauty Facts, Open Pet Food Facts, and Open Products Facts).

> **Status & Help Wanted:** Right now, we do **not** have an active group of volunteers working on these imports. Everything here is very much a work in progress, and we would genuinely welcome your help — whether you are technical or not.

If you want to get involved or have questions, check the [Data Imports wiki page](https://wiki.openfoodfacts.org/Data_imports) and come say hello on [Open Food Facts Slack](https://slack.openfoodfacts.org) (for example in `#producers-platform` or `#data-quality`).

## Ways You Can Help

You don't need to know how to code to contribute here. Here are the main areas where we are looking for help:

1. **Finish the USDA import (80–90% ready)**
   The USDA FoodData Central import is already 80–90% complete. The team is happy to spend time mentoring anyone willing to help get it across the finish line.
   → See [Open Data Imports & Quality Checks](docs/open-data-imports.md)

2. **Hunt and document new open datasets**
   Help us find new open food/product datasets (typically on national open data portals or public registries) and document them in this repository.
   → See [Open Data Imports & Quality Checks](docs/open-data-imports.md)

3. **Check data quality before pushing to production**
   Before any imported dataset goes live on Open Food Facts, checking data quality on the platform is an essential step.
   → See [Open Data Imports & Quality Checks](docs/open-data-imports.md)

4. **Engage food producers**
   Help reach out to and onboard food producers so they can share their product data directly, following the steps on the [Producers' data wiki page](https://wiki.openfoodfacts.org/Producers%27_data).
   → See [Producer Outreach](docs/producer-outreach.md)

5. **Wire incoming GS1 / FTP producer feeds**
   If you are comfortable with backend/data engineering, we need help wiring incoming producer data—including files delivered to Open Food Facts's FTP in GS1 format (typically XML)—into `openfoodfacts-server`.
   → See [GS1 & FTP Producer Feeds](docs/gs1-and-ftp.md)

## How Imports Typically Work

In short, the usual goal for an import is to generate a **CSV file** that can be loaded into the Open Food Facts Producer Platform under a bespoke organisation, review its data quality on the platform, and then push it to production. (Note: using a bespoke organisation on the Producer Platform currently raises issues with excessive data protection, so we may end up taking a different route.)

For more details, see:
- [Open Data Imports & Quality Checks](docs/open-data-imports.md)
- [Producer Outreach](docs/producer-outreach.md)
- [GS1 & FTP Producer Feeds](docs/gs1-and-ftp.md)
- [Data Formats](docs/data-formats.md) & [Quality Guidelines](docs/quality-guidelines.md) (detailed reference)
- [Contributing Guide](CONTRIBUTING.md)

## What's in This Repository

- `databases/` – Public & government database imports (e.g. [EU EPREL](databases/eprel/README.md))
- `producers/` – Data from food producers (e.g. [KFC](producers/kfc/README.md))
- `apps/` – Data from partner apps (e.g. `apps/scanoid/`)
- `labels/` – Label and certification data
- `research/` – Academic and research datasets
- `templates/` – Starter templates for documenting a new dataset
- `docs/` – Guides and reference documentation

## License

The Open Food Facts database is licensed under the [Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/). Individual datasets in this repository may carry their own licenses—check each directory's `README.md`.
