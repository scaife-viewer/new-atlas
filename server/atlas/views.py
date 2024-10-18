from django.views.generic import TemplateView

from .alignments.models import TextAlignment
from .annotations.models import TextAnnotationCollection
from .ctslibrary.precomputed import library_view_json
from .dictionaries.models import Dictionary
from .morphology.models import Form, Lemma
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
        }

    def library(self):
        return library_view_json()
