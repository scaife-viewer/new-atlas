from django.views.generic import ListView, DetailView, TemplateView

from .models import TextAnnotationCollection, TextAnnotation


class TextAnnotationCollectionListView(ListView):
    model = TextAnnotationCollection


class TextAnnotationDetailView(DetailView):
    slug_field = "urn"
    slug_url_kwarg = "urn"
    model = TextAnnotation
