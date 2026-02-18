"""Field Operations Hub models: daily logs, time tracking, expenses."""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone as django_tz

from apps.core.models import TenantModel


class DailyLog(TenantModel):
    """Daily field log entry — one per project per day."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"

    class DelayReason(models.TextChoices):
        WEATHER = "weather", "Weather"
        MATERIAL = "material", "Material Delay"
        LABOR = "labor", "Labor Shortage"
        INSPECTION = "inspection", "Inspection"
        CLIENT = "client", "Client Decision"
        PERMIT = "permit", "Permit Issue"
        EQUIPMENT = "equipment", "Equipment Failure"
        NONE = "none", "No Delay"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="daily_logs",
    )
    log_date = models.DateField()
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_daily_logs",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    # Weather as structured JSON: {temp_high, temp_low, conditions, wind, precipitation}
    weather_conditions = models.JSONField(default=dict, blank=True)

    work_performed = models.TextField(blank=True)
    issues_encountered = models.TextField(blank=True)
    delays = models.TextField(blank=True)
    delay_reason = models.CharField(
        max_length=20,
        choices=DelayReason.choices,
        default=DelayReason.NONE,
    )

    # Structured lists: [{name, company, time_in, time_out, purpose}]
    visitors = models.JSONField(default=list, blank=True)
    # Structured lists: [{description, vendor, quantity, condition}]
    material_deliveries = models.JSONField(default=list, blank=True)

    safety_incidents = models.BooleanField(default=False)

    # M2M to documents.Photo (use distinct name to avoid clash with linked_daily_log FK reverse)
    attached_photos = models.ManyToManyField(
        "documents.Photo",
        blank=True,
        related_name="daily_log_attachments",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_daily_logs",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [["project", "log_date"]]
        ordering = ["-log_date"]
        indexes = [
            models.Index(fields=["organization", "log_date"], name="fops_log_org_date_idx"),
            models.Index(fields=["organization", "status"], name="fops_log_org_status_idx"),
            models.Index(fields=["project", "log_date"], name="fops_log_proj_date_idx"),
        ]

    def __str__(self):
        return f"{self.project} — {self.log_date}"


class DailyLogCrewEntry(models.Model):
    """Crew count and hours worked within a daily log."""

    daily_log = models.ForeignKey(
        DailyLog,
        on_delete=models.CASCADE,
        related_name="crew_entries",
    )
    crew_or_trade = models.CharField(max_length=100)
    worker_count = models.PositiveIntegerField(default=1)
    hours_worked = models.DecimalField(max_digits=6, decimal_places=2)
    work_description = models.TextField(blank=True)

    class Meta:
        ordering = ["crew_or_trade"]
        verbose_name_plural = "Daily log crew entries"

    def __str__(self):
        return f"{self.crew_or_trade} × {self.worker_count} ({self.hours_worked}h)"


class TimeEntry(TenantModel):
    """Employee time-tracking entry with mobile clock in/out and GPS support."""

    class EntryType(models.TextChoices):
        CLOCK = "clock", "Clock In/Out"
        MANUAL = "manual", "Manual Entry"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="time_entries",
    )
    cost_code = models.ForeignKey(
        "financials.CostCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )
    date = models.DateField()
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Calculated from clock_in/out or entered manually.",
    )
    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
        default=EntryType.CLOCK,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # GPS data: {lat, lng, accuracy}
    gps_clock_in = models.JSONField(null=True, blank=True)
    gps_clock_out = models.JSONField(null=True, blank=True)
    is_within_geofence = models.BooleanField(null=True, blank=True)

    overtime_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notes = models.TextField(blank=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_time_entries",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date", "-clock_in"]
        verbose_name_plural = "time entries"
        indexes = [
            models.Index(fields=["organization", "user", "date"], name="fops_te_org_user_date_idx"),
            models.Index(fields=["organization", "status"], name="fops_te_org_status_idx"),
            models.Index(fields=["project", "date"], name="fops_te_proj_date_idx"),
        ]

    def __str__(self):
        return f"{self.user} — {self.project} — {self.date} ({self.hours}h)"

    def calculate_hours(self):
        """Compute hours from clock_in/clock_out. Returns 0 if not clocked out."""
        if self.clock_in and self.clock_out:
            delta = self.clock_out - self.clock_in
            return Decimal(str(round(delta.total_seconds() / 3600, 2)))
        return Decimal("0.00")


class ExpenseEntry(TenantModel):
    """Field expense tracking with receipt capture."""

    class Category(models.TextChoices):
        MATERIAL = "material", "Material"
        FUEL = "fuel", "Fuel"
        MEALS = "meals", "Meals"
        TOOLS = "tools", "Tools"
        EQUIPMENT_RENTAL = "equipment_rental", "Equipment Rental"
        SUPPLIES = "supplies", "Supplies"
        MILEAGE = "mileage", "Mileage"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REIMBURSED = "reimbursed", "Reimbursed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_entries",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="expense_entries",
    )
    cost_code = models.ForeignKey(
        "financials.CostCode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expense_entries",
    )
    date = models.DateField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True,
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # S3 key for receipt image (same pattern as documents app)
    receipt_file_key = models.CharField(max_length=500, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Only used when category == MILEAGE
    mileage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Miles driven (when category is MILEAGE).",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expense_entries",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "expense entries"
        indexes = [
            models.Index(fields=["organization", "user", "date"], name="fops_exp_org_user_date_idx"),
            models.Index(fields=["organization", "status"], name="fops_exp_org_status_idx"),
            models.Index(fields=["project", "date"], name="fops_exp_proj_date_idx"),
        ]

    def __str__(self):
        return f"{self.description} — ${self.amount}"
