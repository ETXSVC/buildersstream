"""Analytics & Reporting Engine admin configuration."""
from django.contrib import admin

from .models import Dashboard, KPI, Report


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ["name", "is_default", "organization", "created_at"]
    list_filter = ["is_default"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at", "created_by"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "is_active", "last_run_at"]
    list_filter = ["report_type", "is_active"]
    search_fields = ["name", "description"]
    readonly_fields = ["last_run_at", "last_run_result", "created_at", "updated_at", "created_by"]


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "value", "target", "unit", "trend", "period_start", "period_end"]
    list_filter = ["category", "trend"]
    search_fields = ["name"]
    readonly_fields = ["trend", "variance_percent", "created_at", "updated_at", "created_by"]
