"""Quality and safety admin configuration."""
from django.contrib import admin

from .models import Inspection, SafetyChecklist, SafetyIncident


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "inspection_type", "status", "scheduled_date"]
    list_filter = ["status", "inspection_type"]


@admin.register(SafetyIncident)
class SafetyIncidentAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "severity", "incident_date", "is_osha_recordable", "is_resolved"]
    list_filter = ["severity", "is_osha_recordable", "is_resolved"]


@admin.register(SafetyChecklist)
class SafetyChecklistAdmin(admin.ModelAdmin):
    list_display = ["name", "is_template", "organization"]
    list_filter = ["is_template"]
