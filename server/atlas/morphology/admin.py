from django.contrib import admin

from .models import Form, Lemma


@admin.register(Lemma)
class LemmaAdmin(admin.ModelAdmin):
    pass


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    raw_id_fields = ("lemma",)
