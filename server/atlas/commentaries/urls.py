from django.urls import path

from .views import CommentaryListView, CommentaryEntryDetailView, passage_view


urlpatterns = [
    path("commentaries/", CommentaryListView.as_view(), name="commentary_list"),
    path("commentaries/passage/<urn>/", passage_view, name="commentary_passage"),
    path(
        "commentaries/entry/<urn>/",
        CommentaryEntryDetailView.as_view(),
        name="commentaryentry_detail",
    ),
]
