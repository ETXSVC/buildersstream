"""Quality & Safety admin configuration."""
from django.contrib import admin

from .models import (
    ChecklistItem,
    Deficiency,
    Inspection,
    InspectionChecklist,
    InspectionResult,
    SafetyIncident,
    ToolboxTalk,
)


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 0
    fields = ["description", "is_required", "sort_order"]
    ordering = ["sort_order"]


@admin.register(InspectionChecklist)
class InspectionChecklistAdmin(admin.ModelAdmin):
    list_display = ["name", "checklist_type", "category", "is_template", "is_active", "organization"]
    list_filter = ["checklist_type", "category", "is_template", "is_active"]
    search_fields = ["name", "description"]
    inlines = [ChecklistItemInline]


class InspectionResultInline(admin.TabularInline):
    model = InspectionResult
    extra = 0
    fields = ["checklist_item", "status", "notes"]
    readonly_fields = ["checklist_item"]


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ["checklist", "project", "inspector", "inspection_date", "status", "overall_score"]
    list_filter = ["status", "checklist__checklist_type", "checklist__category"]
    search_fields = ["checklist__name", "project__name", "notes"]
    date_hierarchy = "inspection_date"
    inlines = [InspectionResultInline]


@admin.register(Deficiency)
class DeficiencyAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "severity", "status", "assigned_to", "due_date"]
    list_filter = ["severity", "status"]
    search_fields = ["title", "description"]
    date_hierarchy = "created_at"


@admin.register(SafetyIncident)
class SafetyIncidentAdmin(admin.ModelAdmin):
    list_display = ["incident_type", "project", "severity", "incident_date", "osha_reportable", "status"]
    list_filter = ["severity", "incident_type", "osha_reportable", "status"]
    search_fields = ["description", "root_cause", "injured_person_name"]
    date_hierarchy = "incident_date"


@admin.register(ToolboxTalk)
class ToolboxTalkAdmin(admin.ModelAdmin):
    list_display = ["topic", "project", "presented_by", "presented_date"]
    list_filter = ["presented_date"]
    search_fields = ["topic", "content"]
    date_hierarchy = "presented_date"
