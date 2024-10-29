from django.db import models

from atlas.texts.models import Node


from sortedm2m.fields import SortedManyToManyField


class AudioAnnotation(models.Model):
    data = models.JSONField(default=dict, blank=True)
    asset_url = models.URLField(max_length=200)
    idx = models.IntegerField(help_text="0-based index")

    text_parts = SortedManyToManyField(
        Node, related_name="audio_annotations"
    )

    urn = models.CharField(max_length=255, blank=True, null=True)

    def resolve_references(self):
        if "references" not in self.data:
            print(f'No references found [urn="{self.urn}"]')
            return
        desired_urns = set(self.data["references"])
        reference_objs = list(Node.objects.filter(urn__in=desired_urns))
        resolved_urns = set([r.urn for r in reference_objs])
        delta_urns = desired_urns.symmetric_difference(resolved_urns)

        if delta_urns:
            print(
                f'Could not resolve all references, probably due to bad data in the CEX file [urn="{self.urn}" unresolved_urns="{",".join(delta_urns)}"]'
            )
        self.text_parts.set(reference_objs)
