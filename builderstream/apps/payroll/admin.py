"""Payroll admin configuration."""
from django.contrib import admin

from .models import CertifiedPayroll, PayPeriod, PayrollRecord


@admin.register(PayPeriod)
class PayPeriodAdmin(admin.ModelAdmin):
    list_display = ["start_date", "end_date", "pay_date", "is_processed"]
    list_filter = ["is_processed"]


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = ["employee", "pay_period", "regular_hours", "overtime_hours", "gross_pay", "net_pay"]


@admin.register(CertifiedPayroll)
class CertifiedPayrollAdmin(admin.ModelAdmin):
    list_display = ["project", "week_ending", "is_submitted"]
    list_filter = ["is_submitted"]
