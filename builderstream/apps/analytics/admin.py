"""Analytics admin configuration."""
from django.contrib import admin

from .models import Dashboard, KPI, Report


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ["name", "is_default", "organization"]
    list_filter = ["is_default"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "is_active"]
    list_filter = ["report_type", "is_active"]


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "value", "target", "period_start", "period_end"]
    list_filter = ["category"]
