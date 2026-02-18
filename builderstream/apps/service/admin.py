"""Service & Warranty Management admin configuration."""
from django.contrib import admin

from .models import ServiceAgreement, ServiceTicket, Warranty, WarrantyClaim


class WarrantyClaimInline(admin.TabularInline):
    model = WarrantyClaim
    extra = 0
    fields = ["description", "status", "cost", "resolution"]
    readonly_fields = ["created_at"]


@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = [
        "ticket_number", "title", "priority", "status", "ticket_type",
        "assigned_to", "scheduled_date", "billable", "total_cost",
    ]
    list_filter = ["status", "priority", "ticket_type", "billable", "billing_type"]
    search_fields = ["ticket_number", "title", "description"]
    readonly_fields = ["ticket_number", "created_at", "updated_at", "created_by"]
    fieldsets = (
        ("Ticket Info", {
            "fields": (
                "ticket_number", "title", "description", "priority", "status",
                "ticket_type", "project", "client",
            )
        }),
        ("Assignment & Schedule", {
            "fields": ("assigned_to", "scheduled_date", "completed_date", "resolution"),
        }),
        ("Billing", {
            "fields": ("billable", "billing_type", "labor_hours", "parts_cost", "total_cost", "invoice"),
        }),
        ("Metadata", {
            "fields": ("organization", "created_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = [
        "description", "project", "warranty_type", "start_date", "end_date", "status",
    ]
    list_filter = ["warranty_type", "status"]
    search_fields = ["description", "manufacturer"]
    readonly_fields = ["created_at", "updated_at", "created_by"]
    inlines = [WarrantyClaimInline]


@admin.register(WarrantyClaim)
class WarrantyClaimAdmin(admin.ModelAdmin):
    list_display = ["warranty", "status", "cost", "created_at"]
    list_filter = ["status"]
    search_fields = ["description", "resolution"]
    readonly_fields = ["created_at", "updated_at", "created_by"]


@admin.register(ServiceAgreement)
class ServiceAgreementAdmin(admin.ModelAdmin):
    list_display = [
        "name", "client", "agreement_type", "status", "billing_frequency",
        "billing_amount", "visits_completed", "visits_per_year", "end_date",
    ]
    list_filter = ["agreement_type", "status", "billing_frequency", "auto_renew"]
    search_fields = ["name"]
    readonly_fields = ["visits_completed", "created_at", "updated_at", "created_by"]
