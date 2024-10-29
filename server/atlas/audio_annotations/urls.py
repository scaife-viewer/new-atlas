from django.urls import path

from .views import AudioAnnotationListView  # , AudioAnnotationDetailView


urlpatterns = [
    path("audio-annotations/", AudioAnnotationListView.as_view(), name="audioannotation_list"),
    # path("audio-annotations/<urn>/", AudioAnnotationDetailView.as_view(), name="audioannotation_detail"),
]
