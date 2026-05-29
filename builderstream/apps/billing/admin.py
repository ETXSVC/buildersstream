"""Billing admin configuration."""
from django.contrib import admin

from .models import Invoice, SubscriptionEvent


@admin.register(SubscriptionEvent)
class SubscriptionEventAdmin(admin.ModelAdmin):
    list_display = ["organization", "event_type", "stripe_event_id", "created_at"]
    list_filter = ["event_type", "created_at"]
    search_fields = ["stripe_event_id", "organization__name"]
    readonly_fields = ["organization", "event_type", "stripe_event_id", "data", "created_at"]
    ordering = ["-created_at"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["organization", "stripe_invoice_id", "amount_due_display", "status", "period_start", "period_end", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["stripe_invoice_id", "organization__name"]
    readonly_fields = ["organization", "stripe_invoice_id", "amount_due", "amount_paid", "currency", "status", "period_start", "period_end", "hosted_invoice_url", "pdf_url", "created_at"]
    ordering = ["-created_at"]

    @admin.display(description="Amount Due")
    def amount_due_display(self, obj):
        return f"${obj.amount_due / 100:.2f}"
