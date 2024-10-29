from django.views.generic import ListView, DetailView

from .models import MetricalAnnotation


class MetricalAnnotationListView(ListView):
    model = MetricalAnnotation


# class MetricalAnnotationDetailView(DetailView):
#     slug_field = "urn"
#     slug_url_kwarg = "urn"
#     model = MetricalAnnotation
