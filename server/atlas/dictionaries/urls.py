from django.urls import path

from .views import (
    DictionaryListView, DictionaryEntryDetailView, HeadwordView, DictionaryEntryWidgetView, CitationListView
)
from .views import dictionary_list, entry_list, lemma_lookup, blank_dictionary_widget


urlpatterns = [
    path("dictionaries/", DictionaryListView.as_view(), name="dictionary_list"),
    path("dictionaries/json", dictionary_list, name="dictionary_list_json"),
    path("dictionaries/entry/<urn>/", DictionaryEntryDetailView.as_view(), name="dictionaryentry_detail"),
    path("dictionaries/widget/", blank_dictionary_widget, name="blank_dictionary_widget"),
    path("dictionaries/widget/lookup/", lemma_lookup, name="lemma_lookup"),
    path("dictionaries/widget/<urn>/", DictionaryEntryWidgetView.as_view(), name="dictionaryentry_widget"),
    path("dictionaries/headword/<headword>/", HeadwordView.as_view(), name="headword_detail"),
    path("dictionaries/citations/", CitationListView.as_view(), name="citation_list"),
    path("dictionaries/<slug:slug>/entries", entry_list, name="entry_list")
]
