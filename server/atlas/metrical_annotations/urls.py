from django.urls import path

from .views import MetricalAnnotationListView  # , MetricalAnnotationDetailView


urlpatterns = [
    path("metrical-annotations/", MetricalAnnotationListView.as_view(), name="metricalannotation_list"),
    # path("metrical-annotations/<urn>/", MetricalAnnotationDetailView.as_view(), name="metricalannotation_detail"),
]
