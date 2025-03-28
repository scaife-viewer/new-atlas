from django.urls import path

from .views import CommentaryListView, CommentaryEntryDetailView


urlpatterns = [
    path("commentaries/", CommentaryListView.as_view(), name="commentary_list"),
    path("commentaries/entry/<urn>/", CommentaryEntryDetailView.as_view(), name="commentaryentry_detail"),
]
