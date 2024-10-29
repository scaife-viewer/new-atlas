from django.db import models

from sortedm2m.fields import SortedManyToManyField

from atlas.texts.models import Node

from atlas.annotations.models import TextAnnotation


IMAGE_ANNOTATION_KIND_CANVAS = "canvas"
IMAGE_ANNOTATION_KIND_CHOICES = ((IMAGE_ANNOTATION_KIND_CANVAS, "Canvas"),)


class ImageAnnotation(models.Model):
    kind = models.CharField(
        max_length=7,
        default=IMAGE_ANNOTATION_KIND_CANVAS,
        choices=IMAGE_ANNOTATION_KIND_CHOICES,
    )
    data = models.JSONField(default=dict, blank=True)
    # @@@ denormed from data
    image_identifier = models.CharField(max_length=255, blank=True, null=True)
    canvas_identifier = models.CharField(max_length=255, blank=True, null=True)
    idx = models.IntegerField(help_text="0-based index")

    text_parts = SortedManyToManyField(Node, related_name="image_annotations")

    urn = models.CharField(max_length=255, blank=True, null=True)


class ImageROI(models.Model):
    # TODO: revisit unique constraints of URN throughout
    urn = models.CharField(max_length=255, blank=True, null=True)

    data = models.JSONField(default=dict, blank=True)

    # @@@ denormed from data; could go away when Django's SQLite backend has proper
    # JSON support
    image_identifier = models.CharField(max_length=255)
    # @@@ this could be structured
    coordinates_value = models.CharField(max_length=255)
    # @@@ idx
    image_annotation = models.ForeignKey(
        ImageAnnotation,
        related_name="roi",
        on_delete=models.CASCADE,
    )

    text_parts = SortedManyToManyField(Node, related_name="roi")
    text_annotations = SortedManyToManyField(TextAnnotation, related_name="roi")
