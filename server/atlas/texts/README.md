# Texts in Scaife

## Overview 
The main purpose of the texts subdirectory is to provide models and ingestion code for texts (e.g. Homer's _Iliad_), as opposed to resources for texts (e.g. commentaries and dictionaries).

## Text Ingestion

To run text ingestion, call `texts.ingestion.ingest_texts()`. Pass `reset=True` if you want to reset the database of texts by deleting the root node.  
  This expects a directory `BASE_DIR.parent/test-data/texts` as `BASE_DIR` is defined in `settings.py`, which currently would be `new-atlas/test-data` (parallel to the `server` directory).  
  The function walks through all directories and files in "texts" and ignores any missing a `metadata.json` file. 
As it walks through subdirectories, it uses the metadata file to create a hierarchically-ordered node for each directory as a "textgroup", "work", or "version" (a textgroup can contain several works, and a work can contain several versions). a Library object is used with the attributes self.text_groups, self.works, and self.versions. 
The versions should be the lowest level of subdirectory. Versions will generally be different translations or editions of texts.  
  A `texts.ingestion.CTSImporter` is used to parse the text files and break them up into the relevant chunks according to CTS format. These chunks of a version of a text are the leaf nodes of the tree structure. Importantly, the ingestion code, for multiple reasons, requires CTS format and the associated URNs. 
The ingestion code generally expects text contents to have a .cex, .tsv, or .txt file extension, and defaults to .txt when this information is not present in matadata.json.  

## The Data Format for Ingestion
All directories in `test-data/texts` must contain a `metadata.json` file. The structure of these directories mirrors that of the nodes in the database (textgroup->work->version files).  
  For instance, we might have a directory `tlg0032` in `test-data/texts`. The directory name is the part of the URN for Xenophon that is specific to Xenophon (the full URN is `urn:cts:greekLit:tlg0032`): this naming convention for directories is recommended but not strictly necessary. The `metadata.json` file in this directory specifies its URN, what kind of node it is (here, a textgroup, corresponding to the works of Xenophon), and other relevant metadata.  
  In this directory we might find another directory `tlg006`, which corresponds to the distinctive part of the URN for Xenophon's _Anabasis_. In the `tlg006` directory we would find another `metadata.json` file indentifying this directory as corresponding an individual work, i.e. _Anabasis_. This directory should not contain further subdirectories. The `metadata.json` file lists all the versions of the work contained in the directory. Each version should be a .cex, .tsv, or .txt file. The recommended naming convention for these files is `<textgroup URN>.<work URN>.<version>.txt`, e.g. `tlg0032.tlg006.perseus-grc2.txt`, where `perseus-grc2` is a string characterizing this version of the work.  
  One thing to note is that, while the metadata file in a textgroup directory need not list all the works contained in the directory, the metadata file in a work directory must list all the versions it contains under the `versions` key. 

## Metadata File
For a textgroup directory, the `metadata.json` file might looks something like:
```
{
  "urn": "urn:cts:greekLit:tlg0032:",
  "node_kind": "textgroup",
  "name": [
    {
      "lang": "eng",
      "value": "Xenophon"
    }
  ]
}
```
For a work directory, the `metadata.json` file might looks something like:
```
{
  "urn": "urn:cts:greekLit:tlg0032.tlg006:",
  "group_urn": "urn:cts:greekLit:tlg0032:",
  "node_kind": "work",
  "lang": "grc",
  "title": [
    {
      "lang": "eng",
      "value": "Anabasis"
    }
  ],
  "versions": [
    {
      "urn": "urn:cts:greekLit:tlg0032.tlg006.perseus-grc2:",
      "node_kind": "version",
      "version_kind": "edition",
      "lang": "grc",
      "first_passage_urn": "urn:cts:greekLit:tlg0032.tlg006.perseus-grc2:1.1.1-1.1.5",
      "citation_scheme": ["book", "chapter", "section"],
      "label": [
        {
          "lang": "eng",
          "value": "Anabasis"
        }
      ],
      "description": [
        {
          "lang": "eng",
          "value": "Xenophon, creator; Xenophontis Opera omnia Volume III Expeditio Cyri; Marchant, E. C. (Edgar Cardew), 1864-1960, editor"
        }
      ]
    }
  ]
}
```
## Version File
A file corresponding to an individual version might look like this (from Perseus' Greek version of Xenophon's _Anabasis_, `tlg0032.tlg006.perseus-grc2.txt`):
```
1.1.1 Δαρείου καὶ Παρυσάτιδος γίγνονται παῖδες δύο, πρεσβύτερος μὲν Ἀρταξέρξης, νεώτερος δὲ Κῦρος· ἐπεὶ δὲ ἠσθένει Δαρεῖος καὶ ὑπώπτευε τελευτὴν τοῦ βίου, ἐβούλετο τὼ παῖδε ἀμφοτέρω παρεῖναι.
1.1.2 ὁ μὲν οὖν πρεσβύτερος παρὼν ἐτύγχανε· Κῦρον δὲ μεταπέμπεται ἀπὸ τῆς ἀρχῆς ἧς αὐτὸν σατράπην ἐποίησε, καὶ στρατηγὸν δὲ αὐτὸν ἀπέδειξε πάντων ὅσοι ἐς Καστωλοῦ πεδίον ἁθροίζονται. ἀναβαίνει οὖν ὁ Κῦρος λαβὼν Τισσαφέρνην ὡς φίλον, καὶ τῶν Ἑλλήνων ἔχων ὁπλίτας ἀνέβη τριακοσίους, ἄρχοντα δὲ αὐτῶν Ξενίαν Παρράσιον.
```
Because this is a .txt file, the ingestion code looks at each line and splits the leading string from the rest of the text. The leading string (here, `1.1.1`) then becomes the portion of the URN identifying a specific section of text, while the rest of the line becomes the text itself.
  For .cex files, the ingestion code instead splits the line at `#`. For instance, a line of the Iliad in .cex format would be:
```
urn:cts:greekLit:tlg0012.tlg001.msA:1.1#Μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος
```
The relevant method in `ingestion.py` for processing individual sections/lines of text is `CTSImporter.extract_urn_and_text_content`.  
