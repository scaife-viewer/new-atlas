from django.urls import path

from .views import NamedEntityCollectionListView, NamedEntityCollectionDetailView


urlpatterns = [
    path("named-entities/", NamedEntityCollectionListView.as_view(), name="namedentitycollection_list"),
    path("named-entities/<urn>/", NamedEntityCollectionDetailView.as_view(), name="namedentitycollection_detail"),
]
