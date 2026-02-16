"""Client portal admin configuration."""
from django.contrib import admin

from .models import ClientPortalAccess, Selection


@admin.register(ClientPortalAccess)
class ClientPortalAccessAdmin(admin.ModelAdmin):
    list_display = ["client_user", "project", "is_active"]
    list_filter = ["is_active"]


@admin.register(Selection)
class SelectionAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "project", "status", "due_date"]
    list_filter = ["status", "category"]
