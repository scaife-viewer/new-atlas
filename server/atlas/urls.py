from django.contrib import admin
from django.urls import include, path

from .views import HomePageView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name="home"),
    path("morphology/", include("atlas.morphology.urls")),
    path("dictionaries/", include("atlas.dictionaries.urls")),
]
