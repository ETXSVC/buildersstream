"""Scheduling admin configuration."""
from django.contrib import admin

from .models import Crew, Equipment, Task, TaskDependency


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ["name", "trade", "foreman", "hourly_rate", "is_active", "organization"]
    list_filter = ["trade", "is_active", "organization"]
    search_fields = ["name"]
    filter_horizontal = ["members"]


class TaskDependencyInline(admin.TabularInline):
    model = TaskDependency
    fk_name = "predecessor"
    extra = 0
    fields = ["successor", "dependency_type", "lag_days"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "name", "project", "task_type", "status", "start_date", "end_date",
        "completion_percentage", "is_critical_path", "float_days", "organization",
    ]
    list_filter = ["status", "task_type", "is_critical_path", "organization"]
    search_fields = ["name", "wbs_code"]
    inlines = [TaskDependencyInline]
    filter_horizontal = ["assigned_users"]
    readonly_fields = [
        "is_critical_path", "float_days",
        "early_start", "early_finish", "late_start", "late_finish",
    ]


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ["predecessor", "successor", "dependency_type", "lag_days"]
    list_filter = ["dependency_type"]


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "name", "equipment_type", "status", "current_project",
        "current_book_value", "next_maintenance", "organization",
    ]
    list_filter = ["status", "equipment_type", "organization"]
    search_fields = ["name", "serial_number"]
    readonly_fields = ["current_book_value"]
