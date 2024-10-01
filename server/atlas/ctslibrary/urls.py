from django.urls import path

from .views import LibraryView, LibraryCollectionView, LibraryPassageView

urlpatterns = [
    path("library/", LibraryView.as_view(), name="library"),
    path("library/<str:urn>/", LibraryCollectionView.as_view(), name="library_collection"),
    path("library/passage/<str:urn>/", LibraryPassageView.as_view(), name="library_passage"),

    path("library/passage/<str:urn>/json/", LibraryPassageView.as_view(format="json"), name="library_passage_json"),
    path("library/passage/<str:urn>/text/", LibraryPassageView.as_view(format="text"), name="library_passage_text"),
    path("library/passage/<str:urn>/xml/", LibraryPassageView.as_view(format="xml"), name="library_passage_xml"),
]
