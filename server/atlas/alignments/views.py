from django.views.generic import ListView

from .models import TextAlignment


class TextAlignmentListView(ListView):
    model = TextAlignment
