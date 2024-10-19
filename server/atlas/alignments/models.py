from django.db import models

from sortedm2m.fields import SortedManyToManyField

from atlas.texts.models import Node, Token


class TextAlignment(models.Model):
    label = models.CharField(blank=True, null=True, max_length=255)
    # description = models.TextField(blank=True, null=True)

    # TODO: Formalize CITE data model for alignments
    urn = models.CharField(max_length=255, unique=True)

    # metadata contains author / attribution information
    metadata = models.JSONField(default=dict, blank=True)

    # versions being sorted maps onto the "items" within a particular record
    versions = SortedManyToManyField(
        "texts.Node", related_name="text_alignments"
    )

    def __str__(self):
        return self.label


class TextAlignmentRecord(models.Model):

    urn = models.CharField(max_length=255, unique=True)
    metadata = models.JSONField(default=dict, blank=True)

    idx = models.IntegerField(help_text="0-based index")

    alignment = models.ForeignKey(TextAlignment, related_name="records", on_delete=models.CASCADE)
    # TODO: Denorm "text part" nodes

    class Meta:
        ordering = ["idx"]


class TextAlignmentRecordRelation(models.Model):
    version = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="alignment_record_relations")
    record = models.ForeignKey(TextAlignmentRecord, on_delete=models.CASCADE, related_name="relations")
    tokens = models.ManyToManyField(Token, related_name="alignment_record_relations")
