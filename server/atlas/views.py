from django.views.generic import TemplateView

from .morphology.models import Form, Lemma


class HomePageView(TemplateView):
    template_name = "home.html"

    def counts(self):
        return {
            "lemmas": Lemma.objects.count(),
            "forms": Form.objects.count(),
        }
