from pathlib import Path

import json
import logging

import jsonlines
from tqdm import tqdm

from django.conf import settings

from atlas.utils import chunked_bulk_create

from .models import Commentary, CommentaryEntry

logger = logging.getLogger(__name__)

commentary_urns = set()


def process_entries(commentary, entries, entry_count=None):
    deferred_entries = []
    logger.info("Extracting entries")
    entry_urns = set()

    with tqdm(total=entry_count) as pbar:
        for e_idx, e in enumerate(entries):
            pbar.update(1)

            assert e["urn"] not in entry_urns

            entry_urns.add(e["urn"])

            entry = CommentaryEntry(
                commentary=commentary,
                idx=e_idx,
                urn=e["urn"],
                corresp=e["corresp"],
                content=e["content"],
                lemma=e["lemma"]
            )
            deferred_entries.append(entry)
    logger.info("Inserting CommentaryEntry objects")
    chunked_bulk_create(CommentaryEntry, deferred_entries)


def _iter_values(paths):
    for path in paths:
        with jsonlines.open(path) as reader:
            for row in reader.iter():
                yield row


def _count_lines(paths):
    count = 0
    for path in paths:
        with jsonlines.open(path) as reader:
            for row in reader.iter():
                count += 1
    return count


def _create_commentary(path):
    logger.debug(f"loading commentary from {path}")
    data = json.load(open(path))

    assert data["urn"] not in commentary_urns

    commentary_urns.add(data["urn"])

    commentary = Commentary.objects.create(
        label=data["label"],
        urn=data["urn"],
    )
    logger.info(f"created commentary {commentary}")
    return commentary, data


def _process_commentary_dir(path):
    logger.debug(f"processing {path}...")
    metadata_path = Path(path, "metadata.json")
    if not metadata_path.exists():
        logger.warning(f"metadata.json not found in {path}")
        return
    commentary, data = _create_commentary(metadata_path)

    entries = data.get("entries")
    if not entries:
        return
    if not isinstance(entries, list):
        entries = [entries]
    entry_paths = [Path(path, e) for e in entries]
    entries = _iter_values(entry_paths)
    entry_count = _count_lines(entry_paths)

    process_entries(commentary, entries, entry_count=entry_count)


def ingest_commentaries(reset=False):
    if reset:
        logger.info("reseting commentaries")
        Commentary.objects.all().delete()

    path = Path(settings.ATLAS_DATA_DIR, "commentaries")

    if path.exists():
        for item in path.iterdir():
            if item.is_dir():
                _process_commentary_dir(item)
    else:
        logger.warning(f"{path} does not exist")
