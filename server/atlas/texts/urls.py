from django.urls import path

from .views import RootNodeListView, NodeDetailView

urlpatterns = [
    path("nodes/", RootNodeListView.as_view(), name="rootnode_list"),
    path("nodes/<urn>/", NodeDetailView.as_view(), name="node_detail"),
]
