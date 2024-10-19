from django.views.generic import DetailView, ListView

from .models import TextAlignment


class TextAlignmentListView(ListView):
    model = TextAlignment


class TextAlignmentDetailView(DetailView):
    slug_field = "urn"
    slug_url_kwarg = "urn"
    model = TextAlignment
