#!/bin/bash
# A script to set up sqlite3 database and necessary directories
# for manage.py runserver to work, and optionally to do ingestion of texts.

SETUP=1
INGEST=0

while [ True ]; do
  if [ "$1" = "-in" -o "$1" = "-ni" ]; then
    INGEST=1
    SETUP=0
    shift 1
  elif [ "$1" = "--ingest" -o "$1" = "-i" ]; then
    INGEST=1
    shift 1
  elif [ "$1" = "--no-setup" -o "$1" = "-n" ]; then
    SETUP=0
    shift 1
  else
    break
  fi
done

if [ $SETUP = 1 ]; then
  if ! [ -d test-data ]; then
    mkdir ./test-data
  fi
  cd server
  mkdir -p ./data/cts
  touch ./data/cts/README.md
  mkdir ./db
  sqlite3 ./db/default.sqlite3 ""
  ./manage.py makemigrations
  ./manage.py migrate
fi

if [ $INGEST = 1 ]; then
  if [ $SETUP = 0 ]; then
    cd server
    rm ./db/default.sqlite3
    sqlite3 ./db/default.sqlite3 ""
    ./manage.py makemigrations
    ./manage.py migrate
  fi
  ./manage.py shell -c "from atlas.texts.ingestion import ingest_texts; ingest_texts(reset=True)"
  ./manage.py shell -c "from atlas.texts.ingestion import tokenize_all_text_parts; tokenize_all_text_parts(reset=True)"
  ./manage.py shell -c "from atlas.dictionaries.ingestion import ingest_dictionaries;  ingest_dictionaries(reset=True)"
fi
