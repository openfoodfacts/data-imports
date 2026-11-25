# GS1 & FTP Producer Feeds

We are looking for contributors able to wire incoming producer data—including files delivered on **Open Food Facts's FTP**—into the Open Food Facts backend.

## What's Needed

Many food producers and data pools export product catalogs in **GS1 format (typically XML)**. We need help building and maintaining the ingestion pipeline that parses these incoming files and maps them into Open Food Facts product records.

## Relevant Pointers in `openfoodfacts-server`

If you want to explore how imports and background tasks work in [`openfoodfacts/openfoodfacts-server`](https://github.com/openfoodfacts/openfoodfacts-server), start here:

- **Core import module:** [`lib/ProductOpener/Import.pm`](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/lib/ProductOpener/Import.pm) — handles data ingestion and updating products in the database.
- **Import scripts:** [`scripts/imports/`](https://github.com/openfoodfacts/openfoodfacts-server/tree/main/scripts/imports) — existing scripts for importing external and structured datasets.
- **Background import/export tasks:** [`docs/dev/how-to-debug-minion-import-and-export-tasks.md`](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/dev/how-to-debug-minion-import-and-export-tasks.md) — explains how asynchronous Minion import jobs are run and debugged.

If you'd like to work on this, come chat with the team on [Open Food Facts Slack](https://slack.openfoodfacts.org) (e.g. `#producers-platform`) or reference the [Data Imports wiki page](https://wiki.openfoodfacts.org/Data_imports).
