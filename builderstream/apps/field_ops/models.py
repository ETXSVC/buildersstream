"""Field operations models: daily logs, time tracking, expenses."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class DailyLog(TenantModel):
    """Daily field log entry."""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="daily_logs")
    date = models.DateField()
    weather = models.CharField(max_length=100, blank=True)
    temperature_high = models.IntegerField(null=True, blank=True)
    temperature_low = models.IntegerField(null=True, blank=True)
    work_summary = models.TextField(blank=True)
    issues = models.TextField(blank=True)
    visitors = models.TextField(blank=True)
    delays = models.TextField(blank=True)
    workers_on_site = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["project", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.project} - {self.date}"


class TimeEntry(TenantModel):
    """Employee time tracking entry."""

    class EntryType(models.TextChoices):
        REGULAR = "regular", "Regular"
        OVERTIME = "overtime", "Overtime"
        DOUBLE_TIME = "double_time", "Double Time"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="time_entries")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="time_entries")
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    entry_type = models.CharField(max_length=20, choices=EntryType.choices, default=EntryType.REGULAR)
    cost_code = models.ForeignKey(
        "estimating.CostCode", on_delete=models.SET_NULL, null=True, blank=True, related_name="time_entries",
    )
    description = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_time_entries",
    )

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "time entries"

    def __str__(self):
        return f"{self.user} - {self.project} - {self.date} ({self.hours}h)"


class Expense(TenantModel):
    """Field expense tracking."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REIMBURSED = "reimbursed", "Reimbursed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="expenses")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="expenses")
    date = models.DateField()
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.FileField(upload_to="receipts/%Y/%m/", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    def __str__(self):
        return f"{self.description} - ${self.amount}"
