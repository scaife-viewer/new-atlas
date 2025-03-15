from django.apps import apps
from django.db.models import Q
from django.views.generic import ListView, DetailView

from .models import Node


class RootNodeListView(ListView):

    def get_queryset(self):
        return Node.get_root_nodes()


class NodeDetailView(DetailView):
    slug_field = "urn"
    slug_url_kwarg = "urn"
    model = Node

    def citations(self):
        urn = self.object.urn
        # urn.version = None
        Citation = apps.get_model("dictionaries.Citation")
        citations = Citation.objects.filter(Q(data__urn=str(urn))|Q(data__urn=str(self.object.urn)))
        return str(urn), citations
