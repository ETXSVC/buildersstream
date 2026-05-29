"""CRM admin configuration — all 7 models with inlines and bulk actions."""
from django.contrib import admin

from .models import (
    AutomationRule,
    Company,
    Contact,
    EmailTemplate,
    Interaction,
    Lead,
    PipelineStage,
)


class InteractionInline(admin.TabularInline):
    """Inline interactions for Contact."""

    model = Interaction
    extra = 0
    fields = ["interaction_type", "direction", "subject", "occurred_at", "logged_by"]
    readonly_fields = ["occurred_at", "logged_by"]


class LeadInline(admin.TabularInline):
    """Inline leads for Contact."""

    model = Lead
    extra = 0
    fields = ["pipeline_stage", "project_type", "estimated_value", "urgency"]
    readonly_fields = ["pipeline_stage"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Contact admin with interactions and leads inlines."""

    list_display = [
        "first_name",
        "last_name",
        "email",
        "company_name",
        "contact_type",
        "lead_score",
        "is_active",
        "created_at",
    ]
    list_filter = ["contact_type", "source", "is_active", "created_at"]
    search_fields = ["first_name", "last_name", "email", "phone", "company_name"]
    readonly_fields = ["lead_score", "created_at", "updated_at"]
    inlines = [LeadInline, InteractionInline]
    fieldsets = (
        ("Basic Info", {"fields": ("first_name", "last_name", "email", "phone", "mobile_phone")}),
        (
            "Company",
            {
                "fields": ("company", "company_name", "job_title"),
            },
        ),
        (
            "Address",
            {
                "fields": ("address_line1", "address_line2", "city", "state", "zip_code"),
                "classes": ("collapse",),
            },
        ),
        (
            "Classification",
            {
                "fields": ("contact_type", "source", "referred_by"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("lead_score", "tags", "custom_fields", "notes", "is_active"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Company admin with contact count."""

    list_display = [
        "name",
        "company_type",
        "phone",
        "email",
        "performance_rating",
        "created_at",
    ]
    list_filter = ["company_type", "created_at"]
    search_fields = ["name", "email", "phone"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Basic Info", {"fields": ("name", "phone", "email", "website", "company_type")}),
        (
            "Address",
            {
                "fields": ("address_line1", "address_line2", "city", "state", "zip_code"),
            },
        ),
        (
            "Compliance",
            {
                "fields": ("insurance_expiry", "license_number", "license_expiry", "performance_rating"),
                "classes": ("collapse",),
            },
        ),
        ("Notes", {"fields": ("notes",)}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    """Pipeline stage admin."""

    list_display = ["name", "sort_order", "color", "is_won_stage", "is_lost_stage", "organization"]
    list_filter = ["is_won_stage", "is_lost_stage"]
    ordering = ["sort_order"]
    fields = ["name", "sort_order", "color", "is_won_stage", "is_lost_stage", "auto_actions"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Lead admin with conversion tracking."""

    list_display = [
        "contact",
        "pipeline_stage",
        "project_type",
        "estimated_value",
        "urgency",
        "assigned_to",
        "last_contacted_at",
        "created_at",
    ]
    list_filter = ["pipeline_stage", "urgency", "project_type", "created_at"]
    search_fields = ["contact__first_name", "contact__last_name", "description"]
    readonly_fields = ["converted_project", "created_at", "updated_at"]
    raw_id_fields = ["contact", "assigned_to", "converted_project"]
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Core",
            {
                "fields": ("contact", "pipeline_stage", "assigned_to"),
            },
        ),
        (
            "Project Details",
            {
                "fields": ("project_type", "estimated_value", "estimated_start", "urgency", "description"),
            },
        ),
        (
            "Loss Tracking",
            {
                "fields": ("lost_reason", "lost_to_competitor"),
                "classes": ("collapse",),
            },
        ),
        (
            "Activity",
            {
                "fields": ("last_contacted_at", "next_follow_up"),
            },
        ),
        (
            "Conversion",
            {
                "fields": ("converted_project",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    """Interaction admin."""

    list_display = ["contact", "interaction_type", "direction", "subject", "occurred_at", "logged_by"]
    list_filter = ["interaction_type", "direction", "occurred_at"]
    search_fields = ["contact__first_name", "contact__last_name", "subject", "body"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["contact", "lead", "logged_by"]
    date_hierarchy = "occurred_at"


@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    """Automation rule admin."""

    list_display = ["name", "trigger_type", "action_type", "is_active", "organization"]
    list_filter = ["trigger_type", "action_type", "is_active"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Rule", {"fields": ("name", "is_active")}),
        ("Trigger", {"fields": ("trigger_type", "trigger_config")}),
        ("Action", {"fields": ("action_type", "action_config")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Email template admin."""

    list_display = ["name", "template_type", "subject", "organization"]
    list_filter = ["template_type"]
    search_fields = ["name", "subject", "body"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Template", {"fields": ("name", "template_type")}),
        ("Content", {"fields": ("subject", "body")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
