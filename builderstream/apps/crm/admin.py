"""CRM admin configuration."""
from django.contrib import admin

from .models import Contact, Deal, PipelineStage


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "company", "contact_type", "is_active"]
    list_filter = ["contact_type", "is_active"]
    search_fields = ["first_name", "last_name", "company", "email"]


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "organization"]
    ordering = ["order"]


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ["title", "contact", "stage", "value", "probability"]
    list_filter = ["stage"]
