from django.views.generic import TemplateView

from .dictionaries.models import Dictionary
from .morphology.models import Form, Lemma


class HomePageView(TemplateView):
    template_name = "home.html"

    def counts(self):
        return {
            "dictionaries": Dictionary.objects.count(),
            "lemmas": Lemma.objects.count(),
            "forms": Form.objects.count(),
        }
