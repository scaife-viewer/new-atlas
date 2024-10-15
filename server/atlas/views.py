from django.views.generic import TemplateView

from .annotations.models import TextAnnotationCollection
from .ctslibrary.precomputed import library_view_json
from .dictionaries.models import Dictionary
from .morphology.models import Form, Lemma
from .texts.models import Node


class HomePageView(TemplateView):
    template_name = "home.html"

    def counts(self):
        return {
            "text_annotation_collections": TextAnnotationCollection.objects.count(),
            "dictionaries": Dictionary.objects.count(),
            "nodes": Node.objects.count(),
            "lemmas": Lemma.objects.count(),
            "forms": Form.objects.count(),
        }

    def library(self):
        return library_view_json()
