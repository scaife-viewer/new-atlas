from pathlib import Path

import json
import logging

import jsonlines

from django.conf import settings


from .models import TextAnnotationCollection, TextAnnotation

# from ..models import Node, TextAnnotation

from atlas.utils import chunked_bulk_create


logger = logging.getLogger(__name__)

# TextAnnotationThroughModel = TextAnnotation.text_parts.through


# def _prepare_text_annotations(path, counters, kind):
#     logger.info(f"Preparing TextAnnotations from {path}")
#     to_create = []
#     for row in load_data(path):
#         urn = row.pop("urn")
#         to_create.append(
#             TextAnnotation(kind=kind, idx=counters["idx"], urn=urn, data=row,)
#         )
#         counters["idx"] += 1
#     return to_create

def process_trees(syntaxtree, trees, tree_count=None):
    deferred = []
    for idx, tree in enumerate(trees):
        urn = tree.pop("urn")
        deferred.append(TextAnnotation(
            idx=idx,
            urn=urn,
            kind="syntax-tree",
            data=tree,
            collection=syntaxtree,
        ))
    chunked_bulk_create(TextAnnotation, deferred)


# # TODO: Determine if we want some of these bulk methods to move to a classmethod
# def _bulk_prepare_text_annotation_through_objects(qs):
#     logger.info("Extracting URNs from text annotation references")
#     qs_with_references = qs.exclude(data__references=None)
#     through_lookup = {}
#     through_values = qs_with_references.values("id", "data__references")
#     urns = set()
#     for row in through_values:
#         through_lookup[row["id"]] = row["data__references"]
#         urns.update(row["data__references"])
#     msg = f"URNs extracted: {len(urns)}"
#     logger.info(msg)

#     logger.info("Building URN to Node pk lookup")
#     node_urn_pk_values = Node.objects.filter(urn__in=urns).values_list("urn", "pk")
#     node_lookup = {}
#     for urn, pk in node_urn_pk_values:
#         node_lookup[urn] = pk

#     logger.info("Preparing through objects for insert")
#     to_create = []
#     for textannotation_id, urns in through_lookup.items():
#         for urn in urns:
#             # TODO: Remove this lookup fallback
#             node_id = node_lookup.get(urn, None)
#             if node_id:
#                 to_create.append(
#                     TextAnnotationThroughModel(
#                         node_id=node_id, textannotation_id=textannotation_id
#                     )
#                 )
#     return to_create


# def _resolve_text_annotation_text_parts(qs):
#     prepared_objs = _bulk_prepare_text_annotation_through_objects(qs)

#     relation_label = TextAnnotationThroughModel._meta.verbose_name_plural
#     msg = f"Bulk creating {relation_label}"
#     logger.info(msg)

#     chunked_bulk_create(TextAnnotationThroughModel, prepared_objs)


def _iter_values(paths):
    for path in paths:
        with jsonlines.open(path) as reader:
            for row in reader.iter():
                yield row


def _create_syntaxtree(path):
    logger.debug(f"loading syntax trees from {path}")
    data = json.load(open(path))
    syntaxtree = TextAnnotationCollection.objects.create(
        label=data["label"],
        urn=data["urn"],
        data={"schemes": data["schemes"]},
    )
    logger.info(f"created syntax trees {syntaxtree}")
    return syntaxtree, data


def _process_syntaxtree_dir(path):
    logger.debug(f"processing {path}...")
    metadata_path = Path(path, "metadata.json")
    if not metadata_path.exists():
        logger.warn(f"metadata.json not found in {path}")
        return
    syntaxtree, data = _create_syntaxtree(metadata_path)

    trees = data.get("trees")
    if not trees:
        return
    if not isinstance(trees, list):
        trees = [trees]
    tree_paths = [Path(path, e) for e in trees]
    trees = _iter_values(tree_paths)

    process_trees(syntaxtree, trees)


def ingest_syntaxtrees(reset=False):
    if reset:
        TextAnnotationCollection.objects.all().delete()

    path = Path(settings.ATLAS_DATA_DIR, "annotations", "syntax-trees")

    if path.exists():
        for item in path.iterdir():
            if item.is_dir():
                _process_syntaxtree_dir(item)

    else:
        logger.warn(f"{path} does not exist")

    # # logger.info("Generating TextAnnotation through models...")
    # # _resolve_text_annotation_text_parts(TextAnnotation.objects.all())
