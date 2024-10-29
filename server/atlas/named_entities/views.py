from django.views.generic import ListView, DetailView, TemplateView

from .models import NamedEntityCollection


class NamedEntityCollectionListView(ListView):
    model = NamedEntityCollection


class NamedEntityCollectionDetailView(DetailView):
    slug_field = "urn"
    slug_url_kwarg = "urn"
    model = NamedEntityCollection
