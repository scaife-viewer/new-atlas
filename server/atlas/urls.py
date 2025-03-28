from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from graphene_django.views import GraphQLView

from .views import HomePageView

urlpatterns = [

    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="graphql_endpoint"),

    path("admin/", admin.site.urls),
    path("", HomePageView.as_view(), name="home"),
    path("", include("atlas.alignments.urls")),
    path("", include("atlas.annotations.urls")),
    path("", include("atlas.attributions.urls")),
    path("", include("atlas.audio_annotations.urls")),
    path("", include("atlas.commentaries.urls")),
    path("", include("atlas.ctslibrary.urls")),
    path("", include("atlas.dictionaries.urls")),
    path("", include("atlas.image_annotations.urls")),
    path("", include("atlas.metrical_annotations.urls")),
    path("", include("atlas.morphology.urls")),
    path("", include("atlas.named_entities.urls")),
    path("", include("atlas.texts.urls")),
]
