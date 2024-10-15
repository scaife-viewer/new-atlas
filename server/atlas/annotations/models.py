from django.db import models


class TextAnnotationCollection(models.Model):

    label = models.CharField(blank=True, null=True, max_length=255)
    data = models.JSONField(default=dict, blank=True)

    urn = models.CharField(max_length=255, unique=True, help_text="urn:cite2:&lt;site>:text_annotation_collection.atlas_v1")

    def __str__(self):
        return self.label

    def annotation_count(self):
        return self.annotations.count()

    # @@@ cache this
    def first_annotation(self):
        return self.annotations.order_by("idx").first()


class TextAnnotation(models.Model):

    kind = models.CharField(max_length=255)
    #     default=hookset.TEXT_ANNOTATION_DEFAULT_KIND,
    #     choices=hookset.TEXT_ANNOTATION_KIND_CHOICES,
    # )
    data = models.JSONField(default=dict, blank=True)
    idx = models.IntegerField(help_text="0-based index")

    urn = models.CharField(max_length=255, blank=True, null=True)

    # text_parts = SortedManyToManyField(
    #     "scaife_viewer_atlas.Node", related_name="text_annotations"
    # )

    # FIXME: Backwards compatibility with other text annotations
    collection = models.ForeignKey(TextAnnotationCollection, related_name="annotations", on_delete=models.CASCADE, blank=True, null=True)

    # def resolve_references(self):
    #     if "references" not in self.data:
    #         print(f'No references found [urn="{self.urn}"]')
    #         return
    #     desired_urns = set(self.data["references"])
    #     reference_objs = list(Node.objects.filter(urn__in=desired_urns))
    #     resolved_urns = set([r.urn for r in reference_objs])
    #     delta_urns = desired_urns.symmetric_difference(resolved_urns)

    #     if delta_urns:
    #         print(
    #             f'Could not resolve all references, probably due to bad data in the CEX file [urn="{self.urn}" unresolved_urns="{",".join(delta_urns)}"]'
    #         )
    #     self.text_parts.set(reference_objs)

    def __str__(self):
        return self.urn

    def prev(self):
        return TextAnnotation.objects.filter(collection=self.collection, idx__lt=self.idx).order_by("-idx").first()
    
    def next(self):
        return TextAnnotation.objects.filter(collection=self.collection, idx__gt=self.idx).order_by("idx").first()
