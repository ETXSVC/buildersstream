"""
Django admin configuration for the clients app.

Registers all 7 models with appropriate list displays, filters,
search fields, and inlines.
"""

from django.contrib import admin

from .models import (
    ClientApproval,
    ClientMessage,
    ClientPortalAccess,
    ClientSatisfactionSurvey,
    PortalBranding,
    Selection,
    SelectionOption,
)


# ---------------------------------------------------------------------------
# ClientPortalAccess
# ---------------------------------------------------------------------------

@admin.register(ClientPortalAccess)
class ClientPortalAccessAdmin(admin.ModelAdmin):
    list_display = [
        "contact", "project", "email", "is_active", "last_login",
        "has_pin", "organization",
    ]
    list_filter = ["is_active", "organization"]
    search_fields = ["email", "contact__first_name", "contact__last_name", "project__name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "access_token", "last_login", "created_at", "updated_at"]
    fieldsets = (
        (None, {
            "fields": ("organization", "contact", "project", "email"),
        }),
        ("Access Control", {
            "fields": ("is_active", "pin_code", "access_token"),
        }),
        ("Permissions", {
            "fields": ("permissions",),
        }),
        ("Metadata", {
            "fields": ("id", "last_login", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def has_pin(self, obj):
        return bool(obj.pin_code)
    has_pin.boolean = True
    has_pin.short_description = "PIN"


# ---------------------------------------------------------------------------
# Selection + SelectionOption inline
# ---------------------------------------------------------------------------

class SelectionOptionInline(admin.TabularInline):
    model = SelectionOption
    extra = 0
    fields = ["name", "price", "price_difference", "is_recommended", "sort_order"]
    readonly_fields = ["id"]
    ordering = ["sort_order"]


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = [
        "name", "category", "project", "status",
        "selected_option", "due_date", "assigned_to_client", "organization",
    ]
    list_filter = ["status", "category", "assigned_to_client", "organization"]
    search_fields = ["name", "description", "project__name"]
    ordering = ["sort_order", "category"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [SelectionOptionInline]
    fieldsets = (
        (None, {
            "fields": ("organization", "project", "category", "name", "description"),
        }),
        ("Status", {
            "fields": ("status", "selected_option", "due_date", "assigned_to_client", "sort_order"),
        }),
        ("Metadata", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(SelectionOption)
class SelectionOptionAdmin(admin.ModelAdmin):
    list_display = [
        "name", "selection", "price", "price_difference",
        "lead_time_days", "supplier", "is_recommended", "sort_order",
    ]
    list_filter = ["is_recommended"]
    search_fields = ["name", "selection__name", "supplier"]
    ordering = ["selection", "sort_order"]
    readonly_fields = ["id", "created_at", "updated_at"]


# ---------------------------------------------------------------------------
# ClientApproval
# ---------------------------------------------------------------------------

@admin.register(ClientApproval)
class ClientApprovalAdmin(admin.ModelAdmin):
    list_display = [
        "title", "approval_type", "project", "contact",
        "status", "requested_at", "expires_at", "reminded_count", "organization",
    ]
    list_filter = ["status", "approval_type", "organization"]
    search_fields = ["title", "description", "project__name", "contact__first_name", "contact__last_name"]
    ordering = ["-requested_at"]
    readonly_fields = [
        "id", "requested_at", "responded_at",
        "reminded_count", "last_reminded_at",
        "created_at", "updated_at",
    ]
    fieldsets = (
        (None, {
            "fields": ("organization", "project", "contact", "approval_type", "title", "description"),
        }),
        ("Source", {
            "fields": ("source_type", "source_id"),
            "classes": ("collapse",),
        }),
        ("Status", {
            "fields": ("status", "expires_at", "requested_at", "responded_at", "response_notes"),
        }),
        ("Signature", {
            "fields": ("client_signature",),
            "classes": ("collapse",),
        }),
        ("Reminders", {
            "fields": ("reminded_count", "last_reminded_at"),
            "classes": ("collapse",),
        }),
        ("Metadata", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# ---------------------------------------------------------------------------
# ClientMessage
# ---------------------------------------------------------------------------

@admin.register(ClientMessage)
class ClientMessageAdmin(admin.ModelAdmin):
    list_display = [
        "subject_display", "project", "sender_type",
        "sender_display", "is_read", "created_at", "organization",
    ]
    list_filter = ["sender_type", "is_read", "organization"]
    search_fields = ["subject", "body", "project__name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "read_at", "created_at", "updated_at"]
    fieldsets = (
        (None, {
            "fields": ("organization", "project", "sender_type", "sender_user", "sender_contact"),
        }),
        ("Message", {
            "fields": ("subject", "body", "attachments"),
        }),
        ("Read Status", {
            "fields": ("is_read", "read_at"),
        }),
        ("Metadata", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def subject_display(self, obj):
        return obj.subject or "(No subject)"
    subject_display.short_description = "Subject"

    def sender_display(self, obj):
        if obj.sender_type == "CONTRACTOR" and obj.sender_user:
            return obj.sender_user.email
        elif obj.sender_type == "CLIENT" and obj.sender_contact:
            return str(obj.sender_contact)
        return "-"
    sender_display.short_description = "Sender"


# ---------------------------------------------------------------------------
# ClientSatisfactionSurvey
# ---------------------------------------------------------------------------

@admin.register(ClientSatisfactionSurvey)
class ClientSatisfactionSurveyAdmin(admin.ModelAdmin):
    list_display = [
        "project", "contact", "milestone", "rating", "nps_score", "submitted_at", "organization",
    ]
    list_filter = ["organization"]
    search_fields = ["project__name", "contact__first_name", "contact__last_name", "milestone", "feedback"]
    ordering = ["-submitted_at"]
    readonly_fields = ["id", "submitted_at", "created_at", "updated_at"]
    fieldsets = (
        (None, {
            "fields": ("organization", "project", "contact", "milestone"),
        }),
        ("Scores", {
            "fields": ("rating", "nps_score", "feedback"),
        }),
        ("Metadata", {
            "fields": ("id", "submitted_at", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# ---------------------------------------------------------------------------
# PortalBranding
# ---------------------------------------------------------------------------

@admin.register(PortalBranding)
class PortalBrandingAdmin(admin.ModelAdmin):
    list_display = [
        "organization", "company_name_override", "primary_color",
        "secondary_color", "has_logo", "custom_domain",
    ]
    list_filter = ["organization"]
    search_fields = ["organization__name", "company_name_override", "custom_domain"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (None, {
            "fields": ("organization", "logo", "company_name_override"),
        }),
        ("Appearance", {
            "fields": ("primary_color", "secondary_color", "welcome_message"),
        }),
        ("White-Label", {
            "fields": ("custom_domain",),
        }),
        ("Metadata", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def has_logo(self, obj):
        return bool(obj.logo)
    has_logo.boolean = True
    has_logo.short_description = "Logo"
