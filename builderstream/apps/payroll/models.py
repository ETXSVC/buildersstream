"""Payroll & Workforce Management models."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Employee(TenantModel):
    """Employee record — may or may not have an app login (user FK)."""

    class EmploymentType(models.TextChoices):
        W2_FULL_TIME = "w2_full_time", "W-2 Full Time"
        W2_PART_TIME = "w2_part_time", "W-2 Part Time"
        CONTRACTOR_1099 = "1099_contractor", "1099 Contractor"

    class Trade(models.TextChoices):
        GENERAL = "general", "General"
        FRAMING = "framing", "Framing"
        ELECTRICAL = "electrical", "Electrical"
        PLUMBING = "plumbing", "Plumbing"
        HVAC = "hvac", "HVAC"
        PAINTING = "painting", "Painting"
        FLOORING = "flooring", "Flooring"
        ROOFING = "roofing", "Roofing"
        CONCRETE = "concrete", "Concrete"
        DRYWALL = "drywall", "Drywall"
        FINISH_CARPENTRY = "finish_carpentry", "Finish Carpentry"
        OTHER = "other", "Other"

    class TaxFilingStatus(models.TextChoices):
        SINGLE = "single", "Single"
        MARRIED_JOINT = "married_joint", "Married Filing Jointly"
        MARRIED_SEPARATE = "married_separate", "Married Filing Separately"
        HEAD_OF_HOUSEHOLD = "head_of_household", "Head of Household"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="employee_profile",
    )
    employee_id = models.CharField(max_length=20, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices, db_index=True,
    )
    trade = models.CharField(max_length=20, choices=Trade.choices, db_index=True)
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # Compensation
    base_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    overtime_rate_multiplier = models.DecimalField(
        max_digits=4, decimal_places=2, default="1.50",
        help_text="Overtime multiplier (e.g., 1.5 for time-and-a-half).",
    )
    burden_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default="0.2800",
        help_text="Burden rate as decimal (e.g., 0.28 = 28% of base for benefits/insurance/taxes).",
    )

    # Compliance (display-only, never store full SSN)
    ssn_last_four = models.CharField(max_length=4, blank=True)
    tax_filing_status = models.CharField(
        max_length=25,
        choices=TaxFilingStatus.choices,
        default=TaxFilingStatus.SINGLE,
    )
    federal_allowances = models.IntegerField(default=0)
    state_allowances = models.IntegerField(default=0)

    # Encrypted sensitive fields (JSON — treat as opaque blob in this implementation)
    direct_deposit_accounts = models.JSONField(
        default=list, blank=True,
        help_text="[{bank_name, routing_number, account_number_last4, allocation_pct}]",
    )

    # Structured data
    certifications = models.JSONField(
        default=list, blank=True,
        help_text="[{name, number, expiry, issuing_body}]",
    )
    emergency_contact = models.JSONField(
        default=dict, blank=True,
        help_text="{name, relationship, phone}",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        unique_together = [("organization", "employee_id")]
        indexes = [
            models.Index(fields=["organization", "trade"], name="payroll_emp_org_trade_idx"),
            models.Index(fields=["organization", "is_active"], name="payroll_emp_org_active_idx"),
            models.Index(fields=["organization", "employment_type"], name="payroll_emp_org_type_idx"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def burdened_rate(self):
        """Base hourly rate * (1 + burden_rate)."""
        return self.base_hourly_rate * (1 + self.burden_rate)


class PayrollRun(TenantModel):
    """A payroll run covering a pay period for all employees."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PROCESSING = "processing", "Processing"
        APPROVED = "approved", "Approved"
        PAID = "paid", "Paid"
        VOID = "void", "Void"

    pay_period_start = models.DateField(db_index=True)
    pay_period_end = models.DateField(db_index=True)
    run_date = models.DateField()
    check_date = models.DateField()
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.DRAFT, db_index=True,
    )

    # Aggregate totals (calculated and stored when run is finalized)
    total_gross = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    total_taxes = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")
    total_net = models.DecimalField(max_digits=12, decimal_places=2, default="0.00")

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_payroll_runs",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-pay_period_end"]
        indexes = [
            models.Index(fields=["organization", "status"], name="payroll_run_org_status_idx"),
            models.Index(fields=["organization", "pay_period_end"], name="payroll_run_org_end_idx"),
        ]

    def __str__(self):
        return f"Payroll {self.pay_period_start} – {self.pay_period_end} ({self.get_status_display()})"


class PayrollEntry(models.Model):
    """Per-employee line item within a PayrollRun.
    NOT a TenantModel — org accessible via payroll_run FK.
    """

    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payroll_entries",
    )

    # Hours
    regular_hours = models.DecimalField(max_digits=6, decimal_places=2, default="0.00")
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default="0.00")
    double_time_hours = models.DecimalField(max_digits=6, decimal_places=2, default="0.00")

    # Pay
    regular_rate = models.DecimalField(max_digits=8, decimal_places=2, default="0.00")
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")

    # Taxes (calculated stubs — would integrate with tax service in production)
    federal_tax = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    state_tax = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    fica = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    medicare = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")

    # Other deductions: [{type, amount}]
    deductions = models.JSONField(default=list, blank=True)

    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")

    # Labor cost allocation to projects/cost codes
    job_cost_allocations = models.JSONField(
        default=list, blank=True,
        help_text="[{project_id, cost_code_id, hours, amount}]",
    )

    class Meta:
        unique_together = [("payroll_run", "employee")]
        ordering = ["employee__last_name", "employee__first_name"]

    def __str__(self):
        return f"{self.employee} – {self.payroll_run}"

    @property
    def total_hours(self):
        return self.regular_hours + self.overtime_hours + self.double_time_hours

    @property
    def total_taxes(self):
        return self.federal_tax + self.state_tax + self.fica + self.medicare

    @property
    def total_deductions_amount(self):
        return sum(d.get("amount", 0) for d in (self.deductions or []))


class CertifiedPayrollReport(TenantModel):
    """WH-347 or state-specific certified payroll report for prevailing wage projects."""

    class ReportType(models.TextChoices):
        WH_347 = "wh_347", "Federal WH-347"
        STATE_SPECIFIC = "state_specific", "State Specific"

    class ReportStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        ACCEPTED = "accepted", "Accepted"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="certified_payroll_reports",
    )
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="certified_reports",
    )
    report_type = models.CharField(
        max_length=20, choices=ReportType.choices, default=ReportType.WH_347,
    )
    week_ending = models.DateField(db_index=True)
    status = models.CharField(
        max_length=15,
        choices=ReportStatus.choices,
        default=ReportStatus.DRAFT,
        db_index=True,
    )
    generated_file_key = models.CharField(
        max_length=500, blank=True,
        help_text="S3 key for the generated PDF.",
    )
    compliance_issues = models.JSONField(
        default=list, blank=True,
        help_text="[{employee_id, trade, hours, paid_rate, required_rate, shortfall}]",
    )

    class Meta:
        ordering = ["-week_ending"]
        indexes = [
            models.Index(fields=["organization", "status"], name="payroll_cpr_org_status_idx"),
            models.Index(fields=["project", "week_ending"], name="payroll_cpr_proj_week_idx"),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} – {self.project} – Week {self.week_ending}"


class PrevailingWageRate(TenantModel):
    """Prevailing wage rate requirements for a project by trade."""

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="prevailing_wage_rates",
    )
    trade = models.CharField(max_length=20, choices=Employee.Trade.choices, db_index=True)
    base_rate = models.DecimalField(max_digits=8, decimal_places=2)
    fringe_rate = models.DecimalField(max_digits=8, decimal_places=2, default="0.00")
    total_rate = models.DecimalField(max_digits=8, decimal_places=2)
    effective_date = models.DateField()

    class Meta:
        ordering = ["-effective_date"]
        unique_together = [("project", "trade", "effective_date")]
        indexes = [
            models.Index(fields=["organization", "project"], name="payroll_pwr_org_proj_idx"),
        ]

    def __str__(self):
        return (
            f"{self.get_trade_display()} – ${self.total_rate}/hr "
            f"(effective {self.effective_date})"
        )

    def save(self, *args, **kwargs):
        self.total_rate = self.base_rate + self.fringe_rate
        super().save(*args, **kwargs)
