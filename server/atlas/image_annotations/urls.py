from django.urls import path

from .views import ImageAnnotationListView  # , ImageAnnotationDetailView


urlpatterns = [
    path("image-annotations/", ImageAnnotationListView.as_view(), name="imageannotation_list"),
    # path("image-annotations/<urn>/", ImageAnnotationDetailView.as_view(), name="imageannotation_detail"),
]
