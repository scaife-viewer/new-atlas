import csv
import os

from atlas import settings

from .models import AudioAnnotation


# @@@ move these constants out to the data
COPYRIGHT_FRAGMENT = "© 2016 David Chamberlain under CC BY 4.0 License, https://creativecommons.org/licenses/by/4.0/"

ANNOTATIONS_DATA_PATH = os.path.join(
    settings.ATLAS_DATA_DIR, "annotations", "audio-annotations"
)

CITE_IDENTIFIER = "urn:cite2:exploreHomer:audio.v1:"


def get_paths():
    if not os.path.exists(ANNOTATIONS_DATA_PATH):
        return []
    return [
        os.path.join(ANNOTATIONS_DATA_PATH, f)
        for f in os.listdir(ANNOTATIONS_DATA_PATH)
        if f.endswith(".csv")
    ]


def _prepare_audio_annotations(path, counters):
    f = open(path)
    reader = csv.reader(f)
    to_create = []
    for row in reader:
        asset_url = row[1]
        data = {"attribution": COPYRIGHT_FRAGMENT, "references": [row[0]]}
        urn = f"{CITE_IDENTIFIER}{counters['idx'] + 1}"
        to_create.append(
            AudioAnnotation(
                idx=counters["idx"], asset_url=asset_url, urn=urn, data=data,
            )
        )
        counters["idx"] += 1
    return to_create


def ingest_audio_annotations(reset=False):
    if reset:
        AudioAnnotation.objects.all().delete()

    to_create = []
    counters = dict(idx=0)
    for path in get_paths():
        to_create.extend(_prepare_audio_annotations(path, counters))

    created = len(AudioAnnotation.objects.bulk_create(to_create, batch_size=500))
    print(f"Created audio annotations [count={created}]")

    for audio_annotation in AudioAnnotation.objects.all():
        audio_annotation.resolve_references()
