# TODO: Expose hooks within `Library` too
import json
import os

from atlas import settings

from .models import AttributionOrganization, AttributionPerson, AttributionRecord


ANNOTATIONS_DATA_PATH = os.path.join(
    settings.ATLAS_DATA_DIR, "annotations", "attributions"
)


def get_paths():
    if not os.path.exists(ANNOTATIONS_DATA_PATH):
        return []
    return [
        os.path.join(ANNOTATIONS_DATA_PATH, f)
        for f in os.listdir(ANNOTATIONS_DATA_PATH)
        if f.endswith(".json")
    ]


def _prepare_attributions(path, counters):
    data = json.load(open(path))
    to_create = []

    # TODO: replace `<type>_cache` with get_or_create
    # TODO: denorm data for orgs / persons too

    org_cache = {}
    pers_cache = {}
    for attribution in data:
        organization = attribution["organization"]
        org_obj = None
        if organization:
            org_name = organization["name"]
            org_obj = org_cache.get(org_name)
            if not org_obj:
                org_obj = AttributionOrganization.objects.create(name=org_name)
                org_cache[org_name] = org_obj
        person = attribution["person"]
        pers_obj = None
        if person:
            pers_name = person["name"]
            pers_obj = pers_cache.get(pers_name)
            if not pers_obj:
                pers_obj = AttributionPerson.objects.create(name=pers_name)
                pers_cache[pers_name] = pers_obj

        role = attribution["role"]
        # TODO: make use of counters[idx]
        to_create.append(
            AttributionRecord(
                role=role,
                person=pers_obj,
                organization=org_obj,
                data=attribution["data"],
            )
        )
    return to_create


def ingest_attributions(reset=False):
    if reset:
        AttributionRecord.objects.all().delete()

    to_create = []
    # TODO: IDX
    counters = dict(idx=0)
    for path in get_paths():
        to_create.extend(_prepare_attributions(path, counters))

    created = len(AttributionRecord.objects.bulk_create(to_create))
    print(f"Created attribution records [count={created}]")

    # TODO: Resolve references
