from django.db import models

from atlas.texts.models import Token


NAMED_ENTITY_KIND_PERSON = "person"
NAMED_ENTITY_KIND_PLACE = "place"
NAMED_ENTITY_KINDS = [
    (NAMED_ENTITY_KIND_PERSON, "Person"),
    (NAMED_ENTITY_KIND_PLACE, "Place"),
]


# TODO: Generic collection / set model
class NamedEntityCollection(models.Model):
    """
    """

    label = models.CharField(blank=True, null=True, max_length=255)
    # TODO: Move out to attributions model
    data = models.JSONField(default=dict, blank=True)

    urn = models.CharField(
        max_length=255,
        unique=True,
        help_text="urn:cite2:<site>:named_entity_collection.atlas_v1",
    )


class NamedEntity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    kind = models.CharField(max_length=6, choices=NAMED_ENTITY_KINDS)
    url = models.URLField(max_length=200)
    data = models.JSONField(default=dict, blank=True)

    idx = models.IntegerField(help_text="0-based index", blank=True, null=True)
    urn = models.CharField(max_length=255, unique=True)

    collection = models.ForeignKey(
        NamedEntityCollection,
        related_name="entities",
        on_delete=models.CASCADE,
    )

    # @@@ we may also want structure these references using URNs
    tokens = models.ManyToManyField(
        Token, related_name="named_entities"
    )

    def __str__(self):
        return f"{self.urn} :: {self.title }"
