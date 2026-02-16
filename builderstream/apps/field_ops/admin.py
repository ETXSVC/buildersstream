"""Field operations admin configuration."""
from django.contrib import admin

from .models import DailyLog, Expense, TimeEntry


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ["project", "date", "weather", "workers_on_site"]
    list_filter = ["date"]


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "date", "hours", "entry_type", "is_approved"]
    list_filter = ["entry_type", "is_approved", "date"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["description", "user", "project", "amount", "status", "date"]
    list_filter = ["status", "category"]
