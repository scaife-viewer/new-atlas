#!/usr/bin/env bash
# A script to set up sqlite3 database and necessary directories
# for manage.py runserver to work, and optionally to do ingestion of texts.
# -s / --setup option forces creation of necessary directories and sqlite3 db.
# -i / --ingest option deletes existing sqlite3 db and ingests texts, dictionaries, and commentaries.
# -d / --dictionary option resets and ingests dictionaries.
# -t / --text option resets and ingests texts.
# -c / --commentary option resets and ingests commentaries.

SETUP=0
INGEST=0
DICT=0
TEXT=0
COMM=0

while [ True ]; do
  if [ "$1" == "-is" -o "$1" == "-si" ]; then
    INGEST=1
    SETUP=1
    shift 1
  elif [ "$1" == "--ingest" -o "$1" == "-i" ]; then
    INGEST=1
    shift 1
  elif [ "$1" == "--setup" -o "$1" == "-s" ]; then
    SETUP=1
    shift 1
  elif [ "$1" == "-d" -o "$1" == "--dictionary" ]; then
    INGEST=0
    DICT=1
  elif [ "$1" == "-t" -o "$1" == "--text" ]; then
    INGEST=0
    TEXT=1
  elif [ "$1" = "-c" -o "$1" == "--commentary" ]; then
    INGEST=0
    COMM=1
  elif [ "$1" == "-ds" -o "$1" == "-sd" ]; then
    INGEST=0
    SETUP=1
    DICT=1
  elif [ "$1" == "-ts" -o "$1" == "-st" ]; then
    INGEST=0
    SETUP=1
    TEXT=1
  elif [ "$1" == "-cs" -o "$1" == "-sc" ]; then
    INGEST=0
    SETUP=1
    COMM=1
  elif [ "$1" == "-dt" -o "$1" == "-td" ]; then
    INGEST=0
    DICT=1
    TEXT=1
  elif [ "$1" == "-dc" -o "$1" == "-cd" ]; then
    INGEST=0
    DICT=1
    COMM=1
  elif [ "$1" == "-tc" -o "$1" == "-ct" ]; then
    INGEST=0
    TEXT=1
    COMM=1
  elif [ "$1" == "-dtc" -o "$1" == "-dct" -o "$1" == "-tcd" -o "$1" == "-tdc" -o "$1" == "-ctd" -o "$1" == "-cdt" ]; then
    INGEST=0
    DICT=1
    TEXT=1
    COMM=1
  else
    break
  fi
done

if ! [ "$(basename "$(pwd)")" == "server" ]; then
  if [ -d server ]; then
    cd server
  else
    echo "no server directory found"
    exit 1
  fi
fi

if [ "$SETUP" = 1 ]; then
  if ! [ -d test-data ]; then
    mkdir ./test-data
    mkdir ./test-data/texts
    mkdir ./test-data/dictionaries
    mkdir ./test-data/commentaries
  fi
  cd server
  mkdir -p ./data/cts
  touch ./data/cts/README.md
  mkdir ./db
  sqlite3 ./db/default.sqlite3 ""
  ./manage.py makemigrations
  ./manage.py migrate
  cd ..
fi

if [ "$INGEST" = 1 ]; then
  if [ "$SETUP" = 0 ]; then
    rm ./db/default.sqlite3
    sqlite3 ./db/default.sqlite3 ""
    ./manage.py makemigrations
    ./manage.py migrate
  fi
  ./manage.py shell -c "from atlas.texts.ingestion import ingest_texts; ingest_texts(reset=True)"
  ./manage.py shell -c "from atlas.texts.ingestion import tokenize_all_text_parts; tokenize_all_text_parts(reset=True)"
  ./manage.py shell -c "from atlas.dictionaries.ingestion import ingest_dictionaries;  ingest_dictionaries(reset=True)"
  ./manage.py shell -c "from atlas.commentaries.ingestion import ingest_commentaries; ingest_commentaries(reset=True)"

else
  if [ "$DICT" = 1 ]; then
    ./manage.py shell -c "from atlas.dictionaries.ingestion import ingest_dictionaries;  ingest_dictionaries(reset=True)"
  fi
  if [ "$TEXT" = 1 ]; then
    ./manage.py shell -c "from atlas.texts.ingestion import ingest_texts; ingest_texts(reset=True)"
    ./manage.py shell -c "from atlas.texts.ingestion import tokenize_all_text_parts; tokenize_all_text_parts(reset=True)"
  fi
  if [ "$COMM" = 1 ]; then
    ./manage.py shell -c "from atlas.commentaries.ingestion import ingest_commentaries; ingest_commentaries(reset=True)"
  fi
fi
