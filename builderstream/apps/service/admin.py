"""Service admin configuration."""
from django.contrib import admin

from .models import ServiceTicket, WarrantyItem


@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "priority", "status", "assigned_to", "scheduled_date"]
    list_filter = ["status", "priority"]
    search_fields = ["title"]


@admin.register(WarrantyItem)
class WarrantyItemAdmin(admin.ModelAdmin):
    list_display = ["item_name", "project", "warranty_start", "warranty_end"]
