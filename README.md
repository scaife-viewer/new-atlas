# Scaife ATLAS v2

Aligned Text and Linguistic Annotation Server

This code is under heavy development and is a step towards one component of Perseus 6.

It is a consolidation and refactoring of backend code from Scaife 1.0 and the Beyond Translation project and will provide the data and services for the reading environment. However, ability to browse the data and annotations is supported and some features of the reading environment are being prototyped here.

To get ATLAS running locally, first run "./startup.sh" to create a sqlite3 database ("/new-atlas/server/db/default.sqlite3") and necessary directories, as well as creating and running Django migrations. If you have files to ingest (e.g. in a directory "new-atlas/test-data/"), instead run "./startup.sh -i". If you've already run "./startup.sh" and want to ingest files, run "./startup.sh -n -i" to skip initial setup.
