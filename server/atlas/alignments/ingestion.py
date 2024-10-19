import json
import os

from atlas import settings

from atlas.texts.models import Node, Token
from atlas.texts.urn import URN

from .models import TextAlignment, TextAlignmentRecord, TextAlignmentRecordRelation


ANNOTATIONS_DATA_PATH = os.path.join(
    settings.ATLAS_DATA_DIR, "annotations", "text-alignments"
)


def get_paths():
    if not os.path.exists(ANNOTATIONS_DATA_PATH):
        return []
    return [
        os.path.join(ANNOTATIONS_DATA_PATH, f)
        for f in os.listdir(ANNOTATIONS_DATA_PATH)
        if f.endswith(".json")
    ]


def process_file(path):
    data = json.load(open(path))

    versions = data["versions"]
    version_objs = []
    for version in versions:
        try:
            version_objs.append(Node.objects.get(urn=version))
        except Node.DoesNotExist:
            print(f"Node with URN {version} not found")

    alignment = TextAlignment(
        label=data["label"],
        urn=data["urn"],
    )

    # TODO: can remove eventually
    if data.get("enable_prototype"):
        alignment.metadata["enable_prototype"] = data["enable_prototype"]
    if data.get("display_options"):
        alignment.metadata["display_options"] = data["display_options"]

    alignment.save()
    alignment.versions.set(version_objs)

    idx = 0
    for row in data["records"]:
        record = TextAlignmentRecord(
            idx=idx,
            alignment=alignment,
            urn=row["urn"],
            metadata=row.get("metadata", {}),
        )
        record.save()
        idx += 1
        for version_obj, relation in zip(version_objs, row["relations"]):
            relation_obj = TextAlignmentRecordRelation(
                version=version_obj, record=record
            )
            relation_obj.save()
            tokens = []
            # TODO: Can we build up a veref map and validate?
            for entry in relation:
                entry_urn = URN(entry)
                ref = entry_urn.passage
                # NOTE: this assumes we're always dealing with a tokenized exemplar, which
                # may not be the case
                text_part_ref, _ = ref.rsplit(".", maxsplit=1)
                text_part_urn = f"{version_obj.urn}{text_part_ref}"
                # TODO: compound Q objects query to minimize round trips
                # print(text_part_urn, ref)
                tokens.append(
                    Token.objects.get(text_part__urn=text_part_urn, ve_ref=ref)
                )
            relation_obj.tokens.set(tokens)


def ingest_alignments(reset=False):
    if reset:
        TextAlignment.objects.all().delete()

    created_count = 0
    for path in get_paths():
        process_file(path)
        created_count += 1
    print(f"Alignments created: {created_count}")
