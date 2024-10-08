from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render
from django.db.models import Subquery, OuterRef, JSONField

from .models import Form, Lemma
from .utils import strip_accents

from atlas.dictionaries.models import DictionaryEntry


SHORT_DEF_DICTS = {
    "grc": "urn:cite2:scaife-viewer:dictionaries.v1:short-def",
    "ang": "urn:cite2:scaife-viewer:dictionaries.v1:ang-short-def",
}


def display_lang(lang):
    return {
        "lat": "Latin",
        "grc": "Ancient Greek",
        "ang": "Old English",
    }.get(lang, lang)


def lemma_list(request):

    lang = request.GET.get("lang", "grc")
    q = request.GET.get("q")

    if q:
        surround = False
        before = None
        after = None
        sq = q = strip_accents(q).lower()
        lemmas = Lemma.objects.filter(lang=lang, unaccented=q).order_by("sort_key")
        if not lemmas.exists():
            lemmas = Lemma.objects.filter(lang=lang, unaccented__startswith=q).order_by("sort_key")
        if not lemmas.exists():
            while q := q[:-1]:
                lemmas = Lemma.objects.filter(lang=lang, unaccented__startswith=q).order_by("sort_key")
                if lemmas.exists():
                    break
            surround = True
            before = lemmas.filter(lang=lang, unaccented__lt=sq).order_by("-sort_key")[:5]
            after = lemmas.filter(lang=lang, unaccented__gt=sq).order_by("sort_key")[:5]
        if lemmas.count() == 1:
            return lemma_detail(request, lemmas.first().pk)
        else:
            return render(request, "morphology/lemma_selection.html", {
                "display_lang": display_lang(lang),
                "lang": lang,
                "lemmas": lemmas,
                "surround": surround,
                "before": before,
                "after": after,
            })
    else:
        page = request.GET.get("page")

        lemmas = Lemma.objects.filter(lang=lang).prefetch_related("forms")
        lemmas = lemmas.order_by("sort_key")

        paginator = Paginator(lemmas, 20)

        try:
            lemmas = paginator.page(page)
        except PageNotAnInteger:
            lemmas = paginator.page(1)
        except EmptyPage:
            lemmas = paginator.page(paginator.num_pages)

        return render(request, "morphology/lemma_list.html", {
            "display_lang": display_lang(lang),
            "lang": lang,
            "lemmas": lemmas,
        })


def lemma_detail(request, pk):

    lemma = get_object_or_404(Lemma, pk=pk)
    forms = lemma.forms.order_by("parse_sort_key", "-count")

    short_def = DictionaryEntry.objects.filter(
        dictionary__urn=SHORT_DEF_DICTS[lemma.lang],
        headword_normalized=lemma.text
    )
    dictionary_entries = DictionaryEntry.objects.filter(
        headword_normalized=lemma.text
    ).exclude(dictionary__urn=SHORT_DEF_DICTS[lemma.lang])

    other_lemmas = Lemma.objects.filter(unaccented=lemma.unaccented).exclude(pk=lemma.pk)

    return render(request, "morphology/lemma_detail.html", {
        "lemma": lemma,
        "forms": forms,
        "other_lemmas": other_lemmas,
        "short_def": short_def,
        "dictionary_entries": dictionary_entries,
    })


def form_list(request):

    lang = request.GET.get("lang", "grc")
    q = request.GET.get("q")

    if q:
        surround = False
        before = None
        after = None
        sq = q = strip_accents(q).lower()

        short_def_subquery = DictionaryEntry.objects.filter(
            dictionary__urn=SHORT_DEF_DICTS[lang],
            headword_normalized=OuterRef("lemma__text")
        ).values("data")[:1]

        forms = Form.objects.filter(unaccented=q).order_by("sort_key")
        if not forms.exists():
            forms = Form.objects.filter(unaccented__startswith=q).order_by("sort_key")
        if not forms.exists():
            while q := q[:-1]:
                forms = Form.objects.filter(unaccented__startswith=q).order_by("sort_key")
                if forms.exists():
                    break
            surround = True
            before = forms.filter(unaccented__lt=sq).order_by("-sort_key")[:5]
            after = forms.filter(unaccented__gt=sq).order_by("sort_key")[:5]
        if forms.count() == 1:
            return form_detail(request, forms.first().pk)
        else:
            return render(request, "morphology/form_selection.html", {
                "display_lang": display_lang(lang),
                "lang": lang,
                "forms": forms,
                "surround": surround,
                "before": before,
                "after": after,
            })

    else:
        page = request.GET.get("page")

        forms = Form.objects.filter(lang=lang).select_related("lemma")
        forms = forms.order_by("sort_key")

        paginator = Paginator(forms, 20)

        try:
            forms = paginator.page(page)
        except PageNotAnInteger:
            forms = paginator.page(1)
        except EmptyPage:
            forms = paginator.page(paginator.num_pages)

        return render(request, "morphology/form_list.html", {
            "display_lang": display_lang(lang),
            "lang": lang,
            "forms": forms,
        })


def form_detail(request, pk):
    form = get_object_or_404(Form, pk=pk)

    short_def = DictionaryEntry.objects.filter(
        dictionary__urn=SHORT_DEF_DICTS[form.lemma.lang],
        headword_normalized=form.lemma.text
    )

    return render(request, "morphology/form_detail.html", {
        "form": form,
        "short_def": short_def,
    })
