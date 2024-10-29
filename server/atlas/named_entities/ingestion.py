import csv
import os
from pathlib import Path

import yaml

from atlas import settings

from atlas.texts.models import Node

from .models import NamedEntity, NamedEntityCollection


NAMED_ENTITIES_DATA_PATH = os.path.join(
    settings.ATLAS_DATA_DIR, "annotations", "named-entities"
)
COLLECTIONS_DIR = os.path.join(NAMED_ENTITIES_DATA_PATH, "processed", "collections")
STANDOFF_DIR = os.path.join(NAMED_ENTITIES_DATA_PATH, "processed", "standoff")


def get_collection_paths():
    if not os.path.exists(COLLECTIONS_DIR):
        return []
    return [
        os.path.join(COLLECTIONS_DIR, f)
        for f in Path(COLLECTIONS_DIR).iterdir()
        if f.suffix in {".yaml", ".yml"}
    ]


def _load_collections(path, lookup):
    with open(path) as f:
        collection_data = yaml.safe_load(f)
        collection = NamedEntityCollection.objects.create(
            label=collection_data["label"],
            urn=collection_data["urn"],
            data=collection_data["metadata"],
        )
        for row in collection_data["entities"]:
            urn = row["urn"]
            # TODO: Revisit this
            named_entity, _ = NamedEntity.objects.get_or_create(
                urn=urn,
                defaults={
                    "title": row["title"],
                    "description": row["description"],
                    "url": row["url"],
                    "kind": row["kind"],
                    "data": row.get("data", {}),
                    "collection": collection,
                },
            )
            lookup[named_entity.urn] = named_entity


def get_standoff_paths():
    if not os.path.exists(STANDOFF_DIR):
        return []
    return [
        os.path.join(STANDOFF_DIR, f)
        for f in os.listdir(STANDOFF_DIR)
        if f.endswith(".csv")
    ]


def _apply_entities(path, lookup):
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            named_entity = lookup[row["named_entity_urn"]]
            text_part = Node.objects.get(urn=row["ref"])
            position = int(row["token_position"])
            tokens = text_part.tokens.filter(position__in=[position])
            named_entity.tokens.add(*tokens)


def ingest_named_entities(reset=False):
    if reset:
        NamedEntityCollection.objects.all().delete()

    lookup = {}
    for path in get_collection_paths():
        _load_collections(path, lookup)

    for path in get_standoff_paths():
        _apply_entities(path, lookup)
