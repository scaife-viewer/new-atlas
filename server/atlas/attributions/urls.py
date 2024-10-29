from django.urls import path

from .views import AttributionRecordListView, AttributionRecordDetailView
from .views import AttributionPersonListView, AttributionPersonDetailView
from .views import AttributionOrganizationListView, AttributionOrganizationDetailView


urlpatterns = [
    path("attributions/", AttributionRecordListView.as_view(), name="attributionrecord_list"),
    path("attributions/people/", AttributionPersonListView.as_view(), name="attributionperson_list"),
    path("attributions/people/<pk>/", AttributionPersonDetailView.as_view(), name="attributionperson_detail"),
    path("attributions/organization/", AttributionOrganizationListView.as_view(), name="attributionorganization_list"),
    path("attributions/organization/<pk>/", AttributionOrganizationDetailView.as_view(), name="attributionorganization_detail"),
    path("attributions/<pk>/", AttributionRecordDetailView.as_view(), name="attributionrecord_detail"),
]
