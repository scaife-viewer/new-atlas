from django.views.generic import TemplateView

from .alignments.models import TextAlignment
from .annotations.models import TextAnnotationCollection
from .attributions.models import AttributionPerson, AttributionOrganization, AttributionRecord
from .audio_annotations.models import AudioAnnotation
from .ctslibrary.precomputed import library_view_json
from .dictionaries.models import Dictionary
from .metrical_annotations.models import MetricalAnnotation
from .morphology.models import Form, Lemma
from .named_entities.models import NamedEntity, NamedEntityCollection
from .texts.models import Node, Token


class HomePageView(TemplateView):
    template_name = "home.html"

    def counts(self):
        return {
            "lemmas": Lemma.objects.count(),
            "forms": Form.objects.count(),

            "tokens": Token.objects.count(),
            "nodes": Node.objects.count(),
            "dictionaries": Dictionary.objects.count(),
            "text_annotation_collections": TextAnnotationCollection.objects.count(),
            "text_alignments": TextAlignment.objects.count(),

            "attribution_people": AttributionPerson.objects.count(),
            "attribution_organizations": AttributionOrganization.objects.count(),
            "attribution_records": AttributionRecord.objects.count(),

            "named_entity_collections": NamedEntityCollection.objects.count(),
            "named_entities": NamedEntity.objects.count(),

            "metrical_annotations": MetricalAnnotation.objects.count(),

            "audio_annotations": AudioAnnotation.objects.count(),
        }

    def library(self):
        return library_view_json()
