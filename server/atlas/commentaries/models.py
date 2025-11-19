# import json

# from django.conf import settings
from django.db import models

# from django.db.models import Q

# from treebeard.mp_tree import Node, MP_Node
# from sortedm2m.fields import SortedManyToManyField


class Commentary(models.Model):
    label = models.CharField(blank=True, null=True, max_length=255)
    data = models.JSONField(default=dict, blank=True)

    urn = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.label

    class Meta:
        verbose_name_plural = "Commentaries"

    def first_entry(self):
        return self.entries.order_by("idx").first()


class CommentaryEntry(models.Model):
    commentary = models.ForeignKey(
        Commentary, related_name="entries", on_delete=models.CASCADE
    )
    idx = models.IntegerField(help_text="0-based index")
    urn = models.CharField(max_length=255, unique=True)
    corresp = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    lemma = models.TextField(blank=True, null=True)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.urn

    class Meta:
        verbose_name_plural = "Commentary Entries"
        unique_together = ("commentary", "idx")

    def previous_entries(self, count):
        return self.commentary.entries.filter(idx__lt=self.idx).order_by("-idx")[
            :count:-1
        ]

    def next_entries(self, count):
        return self.commentary.entries.filter(idx__gt=self.idx).order_by("idx")[:count]

    def to_dict(self):
        return dict(
            idx=self.idx,
            urn=self.urn,
            corresp=self.corresp,
            content=self.content,
            data=self.data,
            lemma=self.lemma,
        )


# @@@ TODO: Node Link
