import json
from django.http import JsonResponse
from django.views.decorators.http import require_safe
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

    def get(self, request, *args, **kwargs):
        object = self.get_object()

        if request.headers.get("accept") == "application/json":
            return JsonResponse(object.to_dict())

        return object


@require_safe
def passage_view(request, urn: str):
    count = request.GET.get("count", 20)
    parsed_urn = cts.URN(urn)
    start_urn = parsed_urn.upTo(parsed_urn.PASSAGE_START)
    start_entry = CommentaryEntry.objects.get(urn=start_urn)
    entries = start_entry.commentary.entries.filter(idx__gte=start_entry.idx).order_by(
        "idx"
    )[:count]

    data = [entry.to_dict() for entry in entries]
    next_idx = data[-1]["idx"] + 1
    prev_idx = max(data[0]["idx"] - (count + 1), 0)

    return JsonResponse({"results": data, "next": next_idx, "previous": prev_idx})
