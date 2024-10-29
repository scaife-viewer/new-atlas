from django.views.generic import ListView, DetailView

from .models import ImageAnnotation


class ImageAnnotationListView(ListView):
    model = ImageAnnotation


# class ImageAnnotationDetailView(DetailView):
#     slug_field = "urn"
#     slug_url_kwarg = "urn"
#     model = ImageAnnotation
