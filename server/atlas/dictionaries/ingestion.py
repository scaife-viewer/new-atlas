from pathlib import Path

import itertools
import json
import logging

from collections import defaultdict

import jsonlines
from tqdm import tqdm

from django.conf import settings

from atlas.utils import (
    normalize_and_strip_marks,
    normalized_no_digits,
    chunked_bulk_create,
)

from .models import Dictionary, DictionaryEntry, Sense, Citation

# # FIXME: Factor out globals into a dictionary-level attr
ROOT_PATH_LOOKUP = []
PARENT_PATH_LOOKUP = defaultdict(dict)
PATH_SET = set()

# the commented line below depends on a line in models.py
# that currently causes "manage.py check" to fail
# CitationThroughModel = Citation.text_parts.through
RESOLVE_CITATIONS_AS_TEXT_PARTS = True

logger = logging.getLogger(__name__)


def _prepare_citation_objs(entry, sense, citations):
    idx = 0
    to_create = []
    for citation in citations:
        citation_obj = Citation(
            label=citation.get("ref", ""),
            entry=entry,
            sense=sense,
            data=citation["data"],
            urn=citation["urn"],
            idx=idx,
        )
        idx += 1
        to_create.append(citation_obj)
    return to_create


def _process_sense(entry, s, idx, parent=None, last_sibling=None):
    senses = []
    citations = []
    if parent is None:
        urn = s["urn"] if s.get("urn") else f"{entry.urn}-n{idx}"
        if ROOT_PATH_LOOKUP:
            last_root = ROOT_PATH_LOOKUP.pop()
            path = last_root._inc_path()
        else:
            path = Sense._get_path(None, 1, 1)
        obj = Sense(
            label=s.get("label", ""),
            definition=s["definition"],
            idx=idx,
            urn=urn,
            depth=1,
            path=path,
        )
        assert path not in PATH_SET
        ROOT_PATH_LOOKUP.append(obj)
    else:
        urn = s["urn"] if s.get("urn") else f"{parent.urn}-n{idx}"
        path = None
        depth = parent.depth + 1
        if last_sibling:
            last_sibling = last_sibling[0]
            if last_sibling.path == parent.path:
                logger.debug("this is the first child of the parent")
                path = Sense._get_path(parent.path, depth, 1)
                assert path not in PATH_SET
                PARENT_PATH_LOOKUP[parent.path].update({depth: path})
            elif last_sibling.depth == depth:
                logger.debug("this is a sibling at the current depth")
                path = last_sibling._inc_path()
                assert path not in PATH_SET
                PARENT_PATH_LOOKUP[parent.path].update({depth: path})
            elif last_sibling.depth > depth:
                logger.debug("this is a node at a higher depth")
                last_sibling_path = PARENT_PATH_LOOKUP[parent.path][depth]
                sibling_obj = Sense(depth=depth, path=last_sibling_path)
                path = sibling_obj._inc_path()
                PARENT_PATH_LOOKUP[parent.path].update({depth: path})
                # last_seen_path = PARENT_PATH_LOOKUP[parent.path][depth]
                # path = Sense._get_path(last_seen_path, depth, 1)
                # this
            else:
                assert False
        else:
            assert False
        logger.debug(path)
        obj = Sense(
            label=entry.dictionary.label,
            definition=s["definition"],
            idx=idx,
            urn=s["urn"],
            depth=depth,
            path=path,
            entry=entry,
        )
        assert path is not None
        PATH_SET.add(obj.path)

    senses.append(obj)

    citations.extend(_prepare_citation_objs(entry, obj, s.get("citations", [])))

    for i, ss in enumerate(s.get("children", [])):
        if i == 0:
            idx += 1
        new_senses, new_citations, idx = _process_sense(
            entry, ss, idx, parent=obj, last_sibling=senses[-1:]
        )
        senses.extend(new_senses)
        citations.extend(new_citations)

    idx += 1
    return senses, citations, idx


# to uncomment the function below, CitationThroughModel in models.py needs to be fixed
# def _bulk_prepare_citation_through_objects(qs):
# logger.info("Retrieving URNs for citations")
# citation_urn_pk_values = qs.values_list("data__urn", "pk")

# candidates = list(set([c[0] for c in citation_urn_pk_values]))
# msg = f"URNs retrieved: {len(candidates)}"
# logger.info(msg)

# logger.info("Building URN to Node (TextPart) pk lookup")
# node_urn_pk_values = Node.objects.filter(urn__in=candidates).values_list(
#    "urn", "pk"
# )
# text_part_lookup = {}
# for urn, pk in node_urn_pk_values:
#    text_part_lookup[urn] = pk

# logger.info("Preparing through objects for insert")
# to_create = []
# for urn, citation_id in citation_urn_pk_values:
#    node_id = text_part_lookup.get(urn, None)
#    if node_id:
#        to_create.append(
#            CitationThroughModel(node_id=node_id, citation_id=citation_id)
#        )
# return to_create

# to uncomment the function below, CitationThroughModel in models.py needs to be fixed
# def _resolve_citation_textparts(qs):
#    prepared_objs = _bulk_prepare_citation_through_objects(qs)
#
#    relation_label = CitationThroughModel._meta.verbose_name_plural
#    msg = f"Bulk creating {relation_label}"
#    logger.info(msg)
#
#    chunked_bulk_create(CitationThroughModel, prepared_objs)


def _defer_entry(deferred, entry, data, s_idx):
    """
    Create entry and related child objects in memory, but don't yet
    persist them to the database.

    This avoids an avalanche of SQL SELECT and INSERT statements that
    would otherwise occur on each `.create` or `.save` call.
    """
    senses = []
    citations = []
    citations.extend(_prepare_citation_objs(entry, None, data.get("citations", [])))
    for sense in data.get("senses", []):
        new_senses, new_citations, s_idx = _process_sense(
            entry, sense, s_idx, parent=None
        )
        senses.extend(new_senses)
        citations.extend(new_citations)
    deferred["entries"].append(entry)
    deferred["senses"].append(senses)
    deferred["citations"].append(citations)
    return s_idx


def flatten_list(nested_list):
    for el in nested_list:
        if hasattr(el, "__getitem__"):
            flatten_list(el)
        else:
            yield el


def process_entries(dictionary, entries, entry_count=None):
    s_idx = 0
    deferred = defaultdict(list)
    logger.info("Extracting entries, senses and citations")
    with tqdm(total=entry_count) as pbar:
        for e_idx, e in enumerate(entries):
            pbar.update(1)
            headword = e["headword"]
            headword_normalized = normalized_no_digits(headword)
            headword_normalized_stripped = normalize_and_strip_marks(headword)
            if e.get("data"):
                intro = e.get("data").get("content")
            elif e.get("definition"):
                intro = e.get("definition")
            else:
                intro = None
            # some jsonl files put most of the data under "data" key,
            # others don't.
            # The solution below is rather crude, but the best one that doesn't involve
            # redoing the jsonl files for e.g. cunliffe-2-hompers
            if "senses" in e.keys():
                data = e
                if data.get("definition"):
                    del data["definition"]
            else:
                data = e["data"] if e.get("data") else e
            # this is for citations not in specific senses
            urn = e["urn"] if e.get("urn") else f"{dictionary.urn}-n{e_idx}"
            entry = DictionaryEntry(
                headword=headword,
                headword_normalized=headword_normalized,
                headword_normalized_stripped=headword_normalized_stripped,
                idx=e_idx,
                urn=urn,
                dictionary=dictionary,
                data=data,
                intro_text=intro,
            )
            s_idx = _defer_entry(deferred, entry, data, s_idx)
    # check to make sure s_idx has been incremented
    prev_idx = -1
    for sense in flatten_list(deferred["senses"]):
        assert sense.idx == prev_idx + 1, "Sense ids have not been incremented properly"
        prev_idx += 1

    logger.info("Inserting DictionaryEntry objects")
    chunked_bulk_create(DictionaryEntry, deferred["entries"])

    logger.info("Setting entry_id on Sense objects")
    entry_urn_pk_lookup = {}
    entry_urn_pk_lookup.update(
        DictionaryEntry.objects.filter(dictionary_id=dictionary.id)
        .order_by("pk")
        .values_list("urn", "pk")
    )

    entry_ids = entry_urn_pk_lookup.values()
    for entry_id, entry_senses in zip(entry_ids, deferred["senses"]):
        for s in entry_senses:
            s.entry_id = entry_id

    logger.info("Inserting Sense objects")
    chunked_bulk_create(Sense, itertools.chain.from_iterable(deferred["senses"]))

    logger.info("Inserting Citation objects")
    chunked_bulk_create(Citation, itertools.chain.from_iterable(deferred["citations"]))


# to uncomment the lines below, CitationThroughModel in models.py needs to be fixed
# if RESOLVE_CITATIONS_AS_TEXT_PARTS:
#    logger.info("Generating citation through models...")
#    citations_with_urns = Citation.objects.filter(
#        sense__entry__dictionary=dictionary
#    ).exclude(data__urn=None)
#    _resolve_citation_textparts(citations_with_urns)


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


def _create_dictionary(path):
    logger.debug(f"loading dictionary from {path}")
    data = json.load(open(path))
    dictionary = Dictionary.objects.create(
        label=data["label"],
        urn=data["urn"],
    )
    logger.info(f"created dictionary {dictionary}")
    return dictionary, data


def _process_dictionary_dir(path):
    logger.debug(f"processing {path}...")
    metadata_path = Path(path, "metadata.json")
    if not metadata_path.exists():
        logger.warning(f"metadata.json not found in {path}")
        return
    dictionary, data = _create_dictionary(metadata_path)

    entries = data.get("entries")
    if not entries:
        return
    if not isinstance(entries, list):
        entries = [entries]
    entry_paths = [Path(path, e) for e in entries]
    entries = _iter_values(entry_paths)
    entry_count = _count_lines(entry_paths)

    process_entries(dictionary, entries, entry_count=entry_count)


def ingest_dictionaries(reset=False):
    if reset:
        Dictionary.objects.all().delete()

    path = Path(settings.ATLAS_DATA_DIR, "dictionaries")

    if path.exists():
        for item in path.iterdir():
            if item.is_dir():
                _process_dictionary_dir(item)
    else:
        logger.warning(f"{path} does not exist")
