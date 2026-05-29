"""Financial Management Suite — Django admin."""
from django.contrib import admin

from .models import (
    Budget,
    ChangeOrder,
    ChangeOrderLineItem,
    CostCode,
    Expense,
    Invoice,
    InvoiceLineItem,
    Payment,
    PurchaseOrder,
    PurchaseOrderLineItem,
)


@admin.register(CostCode)
class CostCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "division", "category", "is_labor", "is_active", "organization"]
    list_filter = ["division", "is_labor", "is_active"]
    search_fields = ["code", "name"]
    ordering = ["division", "code"]


class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 0
    fields = ["description", "cost_code", "budget_type", "budgeted_amount", "actual_amount", "variance_amount"]
    readonly_fields = ["variance_amount", "variance_percent"]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["description", "project", "cost_code", "budgeted_amount", "actual_amount", "variance_amount"]
    list_filter = ["budget_type", "organization"]
    search_fields = ["description", "project__name"]
    readonly_fields = ["variance_amount", "variance_percent"]
    ordering = ["project", "cost_code"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["description", "project", "expense_type", "amount", "expense_date", "approval_status", "vendor_name"]
    list_filter = ["expense_type", "approval_status", "organization"]
    search_fields = ["description", "vendor_name", "project__name"]
    ordering = ["-expense_date"]
    date_hierarchy = "expense_date"


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    fields = ["description", "quantity", "unit", "unit_price", "line_total", "sort_order"]
    readonly_fields = ["line_total"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "project", "invoice_type", "status", "total", "balance_due", "due_date"]
    list_filter = ["status", "invoice_type", "organization"]
    search_fields = ["invoice_number", "sent_to_email", "project__name"]
    readonly_fields = ["invoice_number", "public_token", "subtotal", "tax_amount", "retainage_amount",
                       "total", "amount_paid", "balance_due", "sent_at", "viewed_at", "view_count"]
    inlines = [InvoiceLineItemInline]
    ordering = ["-created_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["invoice", "project", "amount", "payment_date", "payment_method", "reference_number"]
    list_filter = ["payment_method", "organization"]
    search_fields = ["reference_number", "invoice__invoice_number"]
    ordering = ["-payment_date"]
    date_hierarchy = "payment_date"


class ChangeOrderLineItemInline(admin.TabularInline):
    model = ChangeOrderLineItem
    extra = 0
    fields = ["description", "cost_code", "quantity", "unit", "unit_cost", "line_total", "sort_order"]
    readonly_fields = ["line_total"]


@admin.register(ChangeOrder)
class ChangeOrderAdmin(admin.ModelAdmin):
    list_display = ["number", "title", "project", "status", "cost_impact", "schedule_impact_days", "submitted_date"]
    list_filter = ["status", "organization"]
    search_fields = ["title", "description", "project__name"]
    readonly_fields = ["cost_impact"]
    inlines = [ChangeOrderLineItemInline]
    ordering = ["project", "number"]


class PurchaseOrderLineItemInline(admin.TabularInline):
    model = PurchaseOrderLineItem
    extra = 0
    fields = ["description", "cost_code", "quantity", "unit", "unit_price", "line_total", "received_quantity", "sort_order"]
    readonly_fields = ["line_total"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["po_number", "project", "vendor_name", "status", "total", "issue_date", "expected_delivery_date"]
    list_filter = ["status", "organization"]
    search_fields = ["po_number", "vendor_name", "project__name"]
    readonly_fields = ["po_number", "subtotal", "total"]
    inlines = [PurchaseOrderLineItemInline]
    ordering = ["-created_at"]
