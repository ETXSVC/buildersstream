"""Project admin configuration."""
from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "number", "organization", "status", "project_type", "contract_amount"]
    list_filter = ["status", "project_type", "is_active"]
    search_fields = ["name", "number"]
