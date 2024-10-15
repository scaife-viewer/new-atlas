from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView

from atlas.utils import strip_accents

from .models import Dictionary, DictionaryEntry

from atlas.morphology.models import Lemma


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
    
    def shortdef(self):
        return DictionaryEntry.objects.filter(
            dictionary__urn="urn:cite2:scaife-viewer:dictionaries.v1:short-def",
            headword_normalized=self.object.headword_normalized
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
            headword_normalized_stripped=sq
        ).first()
        if entry:
            return redirect("dictionaryentry_widget", urn=entry.urn)


class HeadwordView(TemplateView):
    template_name = "dictionaries/headword_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['headword'] = self.kwargs['headword']
        context['entries'] = DictionaryEntry.objects.filter(
            headword_normalized=self.kwargs['headword']
        )
        context['shortdef'] = DictionaryEntry.objects.filter(
            dictionary__urn="urn:cite2:scaife-viewer:dictionaries.v1:short-def",
            headword_normalized=self.kwargs['headword']
        )
        context['lemmas'] = Lemma.objects.filter(text=self.kwargs['headword'])
        return context
