from django.urls import path


from .views import form_detail, form_list, lemma_detail, lemma_list

urlpatterns = [
    path("lemmas/", lemma_list, name="lemma_list"),
    path("lemma/<pk>/", lemma_detail, name="lemma_detail"),
    path("forms/", form_list, name="form_list"),
    path("form/<pk>/", form_detail, name="form_detail"),
]
