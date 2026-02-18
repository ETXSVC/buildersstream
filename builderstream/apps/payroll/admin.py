"""Payroll & Workforce Management admin configuration."""
from django.contrib import admin

from .models import (
    CertifiedPayrollReport,
    Employee,
    PayrollEntry,
    PayrollRun,
    PrevailingWageRate,
)


class PayrollEntryInline(admin.TabularInline):
    model = PayrollEntry
    extra = 0
    fields = [
        "employee",
        "regular_hours", "overtime_hours", "double_time_hours",
        "regular_rate", "gross_pay",
        "federal_tax", "state_tax", "fica", "medicare",
        "net_pay",
    ]
    readonly_fields = ["net_pay"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        "employee_id", "last_name", "first_name", "trade",
        "employment_type", "base_hourly_rate", "is_active", "hire_date",
    ]
    list_filter = ["trade", "employment_type", "is_active", "organization"]
    search_fields = ["first_name", "last_name", "email", "employee_id"]
    ordering = ["organization", "last_name", "first_name"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        ("Identity", {
            "fields": [
                "organization", "user", "employee_id",
                "first_name", "last_name", "email", "phone",
            ],
        }),
        ("Employment", {
            "fields": ["employment_type", "trade", "hire_date", "termination_date", "is_active"],
        }),
        ("Compensation", {
            "fields": ["base_hourly_rate", "overtime_rate_multiplier", "burden_rate"],
        }),
        ("Tax Information", {
            "fields": [
                "ssn_last_four", "tax_filing_status",
                "federal_allowances", "state_allowances",
            ],
            "classes": ["collapse"],
        }),
        ("Financial & HR Data", {
            "fields": ["direct_deposit_accounts", "certifications", "emergency_contact"],
            "classes": ["collapse"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = [
        "pay_period_start", "pay_period_end", "check_date",
        "status", "total_gross", "total_net",
    ]
    list_filter = ["status", "organization"]
    ordering = ["-pay_period_end"]
    readonly_fields = [
        "total_gross", "total_taxes", "total_deductions", "total_net",
        "approved_at", "created_at", "updated_at",
    ]
    inlines = [PayrollEntryInline]
    fieldsets = [
        ("Pay Period", {
            "fields": [
                "organization", "pay_period_start", "pay_period_end",
                "run_date", "check_date",
            ],
        }),
        ("Status", {
            "fields": ["status", "approved_by", "approved_at", "notes"],
        }),
        ("Totals", {
            "fields": ["total_gross", "total_taxes", "total_deductions", "total_net"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]


@admin.register(CertifiedPayrollReport)
class CertifiedPayrollReportAdmin(admin.ModelAdmin):
    list_display = [
        "project", "payroll_run", "report_type",
        "week_ending", "status", "issue_count",
    ]
    list_filter = ["status", "report_type", "organization"]
    ordering = ["-week_ending"]
    readonly_fields = ["created_at", "updated_at"]

    @admin.display(description="Issues")
    def issue_count(self, obj):
        return len(obj.compliance_issues or [])


@admin.register(PrevailingWageRate)
class PrevailingWageRateAdmin(admin.ModelAdmin):
    list_display = ["project", "trade", "base_rate", "fringe_rate", "total_rate", "effective_date"]
    list_filter = ["trade", "organization"]
    ordering = ["project", "trade", "-effective_date"]
    readonly_fields = ["total_rate", "created_at", "updated_at"]
