"""Field operations admin configuration."""
from django.contrib import admin

from .models import DailyLog, DailyLogCrewEntry, ExpenseEntry, TimeEntry


class DailyLogCrewEntryInline(admin.TabularInline):
    model = DailyLogCrewEntry
    extra = 1
    fields = ["crew_or_trade", "worker_count", "hours_worked", "work_description"]


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ["project", "log_date", "status", "submitted_by", "safety_incidents"]
    list_filter = ["status", "delay_reason", "safety_incidents", "log_date"]
    search_fields = ["project__name", "work_performed"]
    date_hierarchy = "log_date"
    raw_id_fields = ["project", "submitted_by", "approved_by"]
    readonly_fields = ["approved_at"]
    inlines = [DailyLogCrewEntryInline]


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "date", "hours", "overtime_hours", "entry_type", "status"]
    list_filter = ["entry_type", "status", "date"]
    search_fields = ["user__email", "project__name", "notes"]
    date_hierarchy = "date"
    raw_id_fields = ["user", "project", "approved_by", "cost_code"]
    readonly_fields = ["approved_at"]


@admin.register(ExpenseEntry)
class ExpenseEntryAdmin(admin.ModelAdmin):
    list_display = ["description", "user", "project", "amount", "category", "status", "date"]
    list_filter = ["status", "category", "date"]
    search_fields = ["description", "user__email", "project__name"]
    date_hierarchy = "date"
    raw_id_fields = ["user", "project", "approved_by", "cost_code"]
    readonly_fields = ["approved_at"]
