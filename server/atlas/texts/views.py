from django.views.generic import ListView, DetailView

from .models import Node


class RootNodeListView(ListView):

    def get_queryset(self):
        return Node.get_root_nodes()


class NodeDetailView(DetailView):
    slug_field = "urn"
    slug_url_kwarg = "urn"
    model = Node
