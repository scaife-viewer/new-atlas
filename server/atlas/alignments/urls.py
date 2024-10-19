from django.urls import path

from .views import TextAlignmentDetailView, TextAlignmentListView


urlpatterns = [
    path("text-alignments/", TextAlignmentListView.as_view(), name="textalignment_list"),
    path("text-alignments/<urn>/", TextAlignmentDetailView.as_view(), name="textalignment_detail"),
]
