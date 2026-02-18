"""Payroll & Workforce Management serializers."""
from rest_framework import serializers

from .models import (
    CertifiedPayrollReport,
    Employee,
    PayrollEntry,
    PayrollRun,
    PrevailingWageRate,
)


# ---------------------------------------------------------------------------
# Employee
# ---------------------------------------------------------------------------

class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    burdened_rate = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Employee
        fields = [
            "id", "employee_id", "first_name", "last_name", "full_name",
            "employment_type", "trade", "hire_date", "is_active",
            "base_hourly_rate", "burdened_rate", "email", "created_at",
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    burdened_rate = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Employee
        fields = [
            "id", "employee_id", "user", "first_name", "last_name", "full_name",
            "email", "phone", "employment_type", "trade",
            "hire_date", "termination_date", "is_active",
            "base_hourly_rate", "overtime_rate_multiplier", "burden_rate", "burdened_rate",
            "ssn_last_four", "tax_filing_status", "federal_allowances", "state_allowances",
            "direct_deposit_accounts", "certifications", "emergency_contact",
            "created_at", "updated_at",
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "employee_id", "user", "first_name", "last_name", "email", "phone",
            "employment_type", "trade", "hire_date",
            "base_hourly_rate", "overtime_rate_multiplier", "burden_rate",
            "ssn_last_four", "tax_filing_status", "federal_allowances", "state_allowances",
            "direct_deposit_accounts", "certifications", "emergency_contact",
        ]


class UpdateCertificationSerializer(serializers.Serializer):
    cert_name = serializers.CharField(max_length=200)
    cert_number = serializers.CharField(max_length=100, allow_blank=True, default="")
    expiry = serializers.DateField()
    issuing_body = serializers.CharField(max_length=200, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# PayrollEntry
# ---------------------------------------------------------------------------

class PayrollEntrySerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    employee_trade = serializers.CharField(source="employee.trade", read_only=True)
    total_hours = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    total_taxes = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PayrollEntry
        fields = [
            "id", "employee", "employee_name", "employee_trade",
            "regular_hours", "overtime_hours", "double_time_hours", "total_hours",
            "regular_rate", "gross_pay",
            "federal_tax", "state_tax", "fica", "medicare", "total_taxes",
            "deductions", "net_pay", "job_cost_allocations",
        ]

    def get_employee_name(self, obj):
        return obj.employee.full_name


class PayrollEntryCreateSerializer(serializers.Serializer):
    """Used when manually adding/overriding an entry."""
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    regular_hours = serializers.DecimalField(max_digits=6, decimal_places=2)
    overtime_hours = serializers.DecimalField(max_digits=6, decimal_places=2, default="0.00")
    double_time_hours = serializers.DecimalField(max_digits=6, decimal_places=2, default="0.00")


# ---------------------------------------------------------------------------
# PayrollRun
# ---------------------------------------------------------------------------

class PayrollRunListSerializer(serializers.ModelSerializer):
    entry_count = serializers.IntegerField(source="entries.count", read_only=True)
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = [
            "id", "pay_period_start", "pay_period_end", "check_date",
            "status", "total_gross", "total_taxes", "total_net",
            "entry_count", "approved_by", "approved_by_name", "created_at",
        ]

    def get_approved_by_name(self, obj):
        if obj.approved_by_id:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}".strip()
        return None


class PayrollRunDetailSerializer(serializers.ModelSerializer):
    entries = PayrollEntrySerializer(many=True, read_only=True)
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = [
            "id", "pay_period_start", "pay_period_end", "run_date", "check_date",
            "status", "total_gross", "total_taxes", "total_deductions", "total_net",
            "approved_by", "approved_by_name", "approved_at", "notes",
            "entries", "created_at", "updated_at",
        ]

    def get_approved_by_name(self, obj):
        if obj.approved_by_id:
            return f"{obj.approved_by.first_name} {obj.approved_by.last_name}".strip()
        return None


class PayrollRunCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = ["pay_period_start", "pay_period_end", "run_date", "check_date", "notes"]


# ---------------------------------------------------------------------------
# CertifiedPayrollReport
# ---------------------------------------------------------------------------

class CertifiedPayrollReportListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    issue_count = serializers.SerializerMethodField()

    class Meta:
        model = CertifiedPayrollReport
        fields = [
            "id", "project", "project_name", "payroll_run",
            "report_type", "week_ending", "status", "issue_count", "created_at",
        ]

    def get_issue_count(self, obj):
        return len(obj.compliance_issues or [])


class CertifiedPayrollReportDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = CertifiedPayrollReport
        fields = [
            "id", "project", "project_name", "payroll_run",
            "report_type", "week_ending", "status",
            "generated_file_key", "compliance_issues",
            "created_at", "updated_at",
        ]


class CertifiedPayrollReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertifiedPayrollReport
        fields = ["project", "payroll_run", "report_type", "week_ending"]


# ---------------------------------------------------------------------------
# PrevailingWageRate
# ---------------------------------------------------------------------------

class PrevailingWageRateSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = PrevailingWageRate
        fields = [
            "id", "project", "project_name", "trade",
            "base_rate", "fringe_rate", "total_rate", "effective_date",
            "created_at",
        ]
        read_only_fields = ["total_rate"]


class PrevailingWageRateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrevailingWageRate
        fields = ["project", "trade", "base_rate", "fringe_rate", "effective_date"]
