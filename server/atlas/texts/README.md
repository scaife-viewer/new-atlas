# atlas.texts

The main purpose of the texts subdirectory is to provide models and ingestion code for texts (e.g. Homer's Iliad), as opposed to resources for texts (e.g. commentaries and dictionaries).

## text ingestion

To run text ingestion, call `texts.ingestion.ingest_texts()`. Pass `reset=True` if you want to reset the database of texts by deleting the root node. 
This expects a directory "BASE_DIR.parent/test-data/texts" as "BASE_DIR" is defined in settings.py, which currently would be "new-atlas/test-data" (parallel to "server" directory).
The function walks through all directories and files in "texts" and ignores any missing a "metadata.json" file. 
As it walks through subdirectories, it uses the metadata file to create a hierarchically-ordered node for each directory as a "textgroup", "work", or "version" (a textgroup can contain several works, and a work can contain several versions). a Library object is used with the attributes self.text_groups, self.works, and self.versions. 
The versions should be the lowest level of subdirectory. Versions will generally be different translations or editions of texts. 
A `texts.ingestion.CTSImporter` is used to parse the text files and break them up into the relevant chunks according to CTS format. These chunks of a version of a text are the leaf nodes of the tree structure. Importantly, the ingestion code, for multiple reasons, requires CTS format and the associated URNs. 
The ingestion code generally expects text conents to have a .cex, .tsv, or .txt file extension, and defaults to .txt when this information is not present in matadata.json. 
