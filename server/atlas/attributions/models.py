from django.db import models
from django.utils.functional import cached_property


from atlas.texts.models import Node


class AttributionPerson(models.Model):
    name = models.CharField(max_length=255)
    # TODO: Consider a CITE URN as well
    orcid_id = models.URLField(max_length=36, blank=True, null=True)  # U


class AttributionOrganization(models.Model):
    name = models.CharField(max_length=255)
    # TODO: Consider a CITE URN as well
    url = models.URLField(max_length=255, blank=True, null=True)  # U


class AttributionRecord(models.Model):
    # TODO: Denorm role into data field
    role = models.CharField(max_length=255)

    person = models.ForeignKey(
        AttributionPerson,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    organization = models.ForeignKey(
        AttributionOrganization,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    # TODO: Enforce person or organization constraint

    data = models.JSONField(default=dict, blank=True)
    # NOTE:
    # data --> references are CTS URNs (maybe database field is too)
    # data --> annotations are CITE URNs (also maybe further modeled in the database)

    # TODO: Formalize relation patterns; we'll query through data.references
    # to begin

    # TODO: IDX
    urns = models.ManyToManyField(
        Node, related_name="attribution_records"
    )

    @cached_property
    def name(self):
        """
        Provides a shortcut for the person / organization related to
        the record
        """
        parts = []
        if self.person:
            parts.append(self.person.name)
        if self.organization:
            parts.append(self.organization.name)
        return ", ".join(parts)
