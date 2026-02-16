"""Scheduling admin configuration."""
from django.contrib import admin

from .models import Crew, ScheduleTask


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ["name", "foreman", "is_active", "organization"]
    list_filter = ["is_active"]


@admin.register(ScheduleTask)
class ScheduleTaskAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "status", "start_date", "end_date", "progress"]
    list_filter = ["status"]
    search_fields = ["name"]
