from django.urls import path

from .views import TextAnnotationCollectionListView, TextAnnotationDetailView


urlpatterns = [
    path("text-annotations/", TextAnnotationCollectionListView.as_view(), name="textannotationcollection_list"),
    path("text-annotations/annotation/<urn>/", TextAnnotationDetailView.as_view(), name="textannotation_detail"),
]
