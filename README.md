# Scaife ATLAS v2

Aligned Text and Linguistic Annotation Server

This code is under heavy development and is a step towards one component of Perseus 6.

It is a consolidation and refactoring of backend code from Scaife 1.0 and the Beyond Translation project and will provide the data and services for the reading environment. However, ability to browse the data and annotations is supported and some features of the reading environment are being prototyped here.

Texts to be ingested should be in jsonl format and be in a directory named
`test-data` parallel to the `server` directory. Ingestion modules will look for subdirectories in `test-data` including `texts` and `dictionaries`.

To get ATLAS running locally, first run `./startup.sh -s` to create a sqlite3
database (`/new-atlas/server/db/default.sqlite3`) and necessary directories,
as well as creating and running Django migrations. If you have files to ingest
(e.g. in a directory `/new-atlas/test-data/`), instead run `./startup.sh -si`.
If you've already run `./startup.sh` and want to ingest files,
run `./startup.sh -i` to skip initial setup.

To ingest just dictionaries, run `./startup.sh -t`, which will reset text
objects in the database and ingest and texts in `test-data/texts`.
Similarly for `./startup.sh -d` and `./startup.sh -c` for dictionaries and
commentaries respectively.

Note that running startup with the "-i" option deletes and recreates the sqlite3 database.

For the setup script to work, it must be possible to run `server/manage.py` in the current environment.
This amounts to `python` being accessible from the CLI in the current environment and Django being installed.

## Adding New CapiTainS Texts

Clone the repo under `server/data/cts` and delete the `cts_resolver_cache` directory
