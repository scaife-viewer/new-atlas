from django.views.generic import ListView, DetailView

from .models import AudioAnnotation


class AudioAnnotationListView(ListView):
    model = AudioAnnotation


# class AudioAnnotationDetailView(DetailView):
#     slug_field = "urn"
#     slug_url_kwarg = "urn"
#     model = AudioAnnotation
