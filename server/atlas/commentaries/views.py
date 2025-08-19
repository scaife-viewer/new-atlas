import json
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.core import serializers

from atlas.ctslibrary import cts

from .models import Commentary, CommentaryEntry


class CommentaryListView(ListView):
    model = Commentary


class CommentaryEntryDetailView(DetailView):
    slug_field = "urn"
    slug_url_kwarg = "urn"
    model = CommentaryEntry

    def previous_entries(self):
        return self.object.previous_entries(1)

    def next_entries(self):
        return self.object.next_entries(1)

    def passage(self):
        return cts.passage_heal(self.object.corresp)[0]

    def get(self, request, *args, **kwargs):
        object = self.get_object()

        if request.headers.get("accept") == "application/json":
            return JsonResponse(object.to_dict())

        return object
