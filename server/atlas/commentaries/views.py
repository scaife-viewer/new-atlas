from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_safe
from django.views.generic import ListView, DetailView

from atlas.ctslibrary import cts

import logging

from .models import Commentary, CommentaryEntry


logger = logging.getLogger(__name__)

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
    page = request.GET.get("page", 1)
    parsed_urn = cts.URN(urn)

    entries = []
    if parsed_urn.reference is not None:
        start_urn = f"{parsed_urn.upTo(parsed_urn.WORK)}:{parsed_urn.reference.start}"
        start_entries = CommentaryEntry.objects.filter(
            corresp__startswith=start_urn
        ).order_by("idx")

        if len(start_entries) == 0:
            logger.error(f"No entries found for {start_urn}")
        else:
            start_entry = start_entries[0]
            entries = start_entry.commentary.entries.filter(idx__gte=start_entry.idx)

    if len(entries) == 0:
        raise Http404

    paginator = Paginator(entries.order_by("idx"), 50)
    page_obj = paginator.get_page(page)

    return JsonResponse(
        {
            "results": list(page_obj.object_list.values()),
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
        }
    )
