import json
from django.apps import apps

from django.db.models import Q

from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from .precomputed import library_view_json
from . import cts
from .utils import apify, encode_link_header, link_passage, normalize_urn


class BaseLibraryView(View):

    format = "html"

    def get(self, request, **kwargs):
        to_response = {"html": self.as_html, "json": self.as_json}.get(
            self.format, "html"
        )
        return to_response()


class LibraryView(BaseLibraryView):

    def as_html(self):
        return render(self.request, "library/index.html", {
            "data": library_view_json()
        })

    def as_json(self):
        data = library_view_json()
        return JsonResponse(data)


class LibraryCollectionView(BaseLibraryView):
    def validate_urn(self):
        if not self.kwargs["urn"].startswith("urn:"):
            raise Http404()

    def get_collection(self):
        self.validate_urn()
        try:
            return cts.collection(self.kwargs["urn"])
        except cts.CollectionDoesNotExist:
            raise Http404()

    @property
    def collection_is_version_exemplar(self):
        return len(str(self.collection.urn).rsplit(".")) > 2

    @property
    def should_redirect_to_reader(self):
        # if settings.SCAIFE_VIEWER_CORE_REDIRECT_VERSION_LIBRARY_COLLECTION_TO_READER:
        #     return self.collection_is_version_exemplar and self.format == "html"
        return False

    def get(self, request, **kwargs):
        self.collection = self.get_collection()
        # if self.should_redirect_to_reader:
        #     return library_text_redirect(request, self.kwargs["urn"])
        return super().get(request, **kwargs)

    def as_html(self):
        normalized_urn = normalize_urn(self.kwargs["urn"])
        if normalized_urn != self.kwargs["urn"]:
            return redirect("library_collection", urn=normalized_urn)

        collection = self.collection
        collection_name = collection.__class__.__name__.lower()
        ctx = {collection_name: collection}
        return render(self.request, f"library/cts_{collection_name}.html", ctx)

    def should_toc(self, collection_obj):
        """
        Only invoke TOC when the collection is a Text.
        """
        return isinstance(collection_obj, cts.Text)

    @property
    def json_payload(self):
        collection = self.collection
        if self.should_toc:
            return apify(collection, with_toc=True)
        return apify(collection)

    def as_json(self):
        try:
            return JsonResponse(self.json_payload)
        except ValueError as e:
            # TODO: see original note
            return JsonResponse({"error": str(e)}, status=500)


# skipping LibraryConditionMixin for now
class LibraryPassageView(View):

    format = "html"

    def get(self, request, **kwargs):
        try:
            passage, healed = self.get_passage()
        except cts.InvalidPassageReference as e:
            return HttpResponse(
                json.dumps({"reason": str(e)}),
                status=400,
                content_type="application/json",
            )
        except cts.InvalidURN as e:
            return HttpResponse(
                json.dumps({"reason": str(e)}),
                status=404,
                content_type="application/json",
            )
        if healed:
            key = {"json": "json_url", "text": "text_url"}.get(self.format, "json")
            redirect = HttpResponse(status=303)
            redirect["Location"] = link_passage(str(passage.urn))[key]
            return redirect
        self.passage = passage
        to_response = {
            "html": self.as_html,
            "json": self.as_json,
            "text": self.as_text,
            "xml": self.as_xml,
        }.get(self.format, "html")
        return to_response()

    def get_passage(self):
        urn = self.kwargs["urn"]
        try:
            return cts.passage_heal(urn)
        except cts.PassageDoesNotExist:
            raise Http404()

    def as_json(self):
        lo = {}
        prev, nxt = self.passage.prev(), self.passage.next()
        if prev:
            lo["prev"] = {
                "target": link_passage(str(prev.urn))["url"],
                "urn": str(prev.urn),
            }
        if nxt:
            lo["next"] = {
                "target": link_passage(str(nxt.urn))["url"],
                "urn": str(nxt.urn),
            }
        response = JsonResponse(apify(self.passage))
        if lo:
            response["Link"] = encode_link_header(lo)
        return response

    def as_text(self):
        return HttpResponse(
            f"{self.passage.content}\n", content_type="text/plain; charset=utf-8"
        )

    def as_xml(self):
        return HttpResponse(f"{self.passage.xml}", content_type="application/xml")
    
    def as_html(self):
        return render(self.request, "library/passage.html", {
            "passage": self.passage,
            "citations": self.citations(),
            "commentary_entries": self.commentary_entries(),
        })
    
    def citations(self):
        urn = self.passage.urn
        urn.version = None
        Citation = apps.get_model("dictionaries.Citation")
        citations = Citation.objects.filter(Q(data__urn=str(urn))|Q(data__urn=str(self.passage.urn)))
        return str(urn), citations

    def commentary_entries(self):
        urn = self.passage.urn
        urn.version = None
        CommentaryEntry = apps.get_model("commentaries.CommentaryEntry")
        commentary_entries = CommentaryEntry.objects.filter(Q(corresp=str(urn))|Q(corresp=str(self.passage.urn)))
        return str(urn), commentary_entries