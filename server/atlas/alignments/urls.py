from django.urls import path

from .views import TextAlignmentListView


urlpatterns = [
    path("text-aligments/", TextAlignmentListView.as_view(), name="textalignment_list"),
]
