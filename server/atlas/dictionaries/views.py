from django.core.paginator import Paginator
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView

from atlas.utils import strip_accents

from .models import Dictionary, DictionaryEntry, Sense, Citation

from atlas.morphology.models import Lemma

# factor these out
SHORT_DEF_DICTS = {
    "grc": "urn:cite2:scaife-viewer:dictionaries.v1:short-def",
    "ang": "urn:cite2:scaife-viewer:dictionaries.v1:ang-short-def",
    "lat": "urn:cite2:scaife-viewer:dictionaries.v1:lat-short-def",
}


class DictionaryListView(ListView):
    model = Dictionary


class DictionaryEntryDetailView(DetailView):
    slug_field = "urn"
    slug_url_kwarg = "urn"
    model = DictionaryEntry

    def previous_entries(self):
        return self.object.previous_entries(10)

    def next_entries(self):
        return self.object.next_entries(10)

    def entry_senses(self):
        return Sense.objects.filter(entry=self.object.pk).filter(depth=1)

    def shortdef(self):
        lang = self.object.dictionary.lang
        return DictionaryEntry.objects.filter(
            dictionary__urn=SHORT_DEF_DICTS.get(lang),
            headword_normalized=self.object.headword_normalized,
        )


class DictionaryEntryWidgetView(DictionaryEntryDetailView):
    template_name = "dictionaries/dictionaryentry_widget.html"

    def previous_entries(self):
        return self.object.previous_entries(1)

    def next_entries(self):
        return self.object.next_entries(1)


def blank_dictionary_widget(request):
    return render(request, "dictionaries/dictionaryentry_widget.html")


def lemma_lookup(request):
    q = request.GET.get("q")

    if q:
        sq = strip_accents(q).lower()

        entry = DictionaryEntry.objects.filter(
            dictionary__urn="urn:cite2:scaife-viewer:dictionaries.v1:montanari",
            headword_normalized_stripped=sq,
        ).first()
        if entry:
            return redirect("dictionaryentry_widget", urn=entry.urn)

    raise Http404("Cannot look up lemma without `q` parameter")


def dictionary_list(request):
    return JsonResponse({"results": list(Dictionary.objects.all().values())})


def entry_list(request, slug):
    try:
        dictionary = Dictionary.objects.get(slug=slug)
    except Dictionary.DoesNotExist as error:
        raise Http404(f"Dictionary {slug} not found")

    q = request.GET.get("q")
    page = request.GET.get("page", 1)

    entries = []
    if q:
        entries = dictionary.search_entries(q)
    else:
        entries = dictionary.entries.all()

    paginator = Paginator(entries.order_by("idx"), 20)
    page_obj = paginator.get_page(page)

    return JsonResponse(
        {
            "results": list(page_obj.object_list.values()),
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
        }
    )


class HeadwordView(TemplateView):
    template_name = "dictionaries/headword_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["headword"] = self.kwargs["headword"]
        context["entries"] = DictionaryEntry.objects.filter(
            headword_normalized=self.kwargs["headword"]
        )
        context["shortdef"] = DictionaryEntry.objects.filter(
            dictionary__urn="urn:cite2:scaife-viewer:dictionaries.v1:short-def",
            headword_normalized=self.kwargs["headword"],
        )
        context["lemmas"] = Lemma.objects.filter(text=self.kwargs["headword"])
        return context


class CitationListView(ListView):
    model = Citation
    paginate_by = 50
