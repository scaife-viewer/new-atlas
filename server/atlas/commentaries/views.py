from django.views.generic import ListView, DetailView

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