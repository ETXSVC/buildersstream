"""Financial admin configuration."""
from django.contrib import admin

from .models import Budget, ChangeOrder, Invoice


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["project", "original_amount", "revised_amount", "actual_cost"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "project", "status", "amount", "due_date"]
    list_filter = ["status"]


@admin.register(ChangeOrder)
class ChangeOrderAdmin(admin.ModelAdmin):
    list_display = ["number", "title", "project", "amount", "status"]
    list_filter = ["status"]
