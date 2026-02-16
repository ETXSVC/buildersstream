"""Payroll models: payroll processing, certified payroll."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class PayPeriod(TenantModel):
    """Pay period definition."""

    start_date = models.DateField()
    end_date = models.DateField()
    pay_date = models.DateField()
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.start_date} to {self.end_date}"


class PayrollRecord(TenantModel):
    """Individual employee payroll record."""

    pay_period = models.ForeignKey(PayPeriod, on_delete=models.CASCADE, related_name="records")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payroll_records")
    regular_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    regular_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    overtime_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.employee} - {self.pay_period}"


class CertifiedPayroll(TenantModel):
    """Certified payroll report for prevailing wage projects."""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="certified_payrolls")
    pay_period = models.ForeignKey(PayPeriod, on_delete=models.CASCADE, related_name="certified_payrolls")
    week_ending = models.DateField()
    contractor_name = models.CharField(max_length=255, blank=True)
    project_name = models.CharField(max_length=255, blank=True)
    is_submitted = models.BooleanField(default=False)
    submitted_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Certified Payroll - {self.project} - {self.week_ending}"
