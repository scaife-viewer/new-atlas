from django.views.generic import ListView, DetailView

from .models import AttributionRecord, AttributionPerson, AttributionOrganization


class AttributionRecordListView(ListView):
    model = AttributionRecord


class AttributionRecordDetailView(DetailView):
    model = AttributionRecord


class AttributionPersonListView(ListView):
    model = AttributionPerson


class AttributionPersonDetailView(DetailView):
    model = AttributionPerson


class AttributionOrganizationListView(ListView):
    model = AttributionOrganization


class AttributionOrganizationDetailView(DetailView):
    model = AttributionOrganization
