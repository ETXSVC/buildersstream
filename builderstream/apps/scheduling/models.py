"""Scheduling & Resource Management models."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Crew(TenantModel):
    """Work crew for resource allocation."""

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

    name = models.CharField(max_length=100)
    trade = models.CharField(max_length=20, choices=Trade.choices, default=Trade.GENERAL)
    foreman = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="crews_led",
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="crews")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(TenantModel):
    """Individual task in the project schedule (Gantt / WBS)."""

    class TaskType(models.TextChoices):
        TASK = "task", "Task"
        MILESTONE = "milestone", "Milestone"
        PHASE = "phase", "Phase"
        SUMMARY = "summary", "Summary"

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"
        CANCELED = "canceled", "Canceled"

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="tasks"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Hierarchy
    parent_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks"
    )
    task_type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.TASK)

    # Schedule
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)
    duration_days = models.IntegerField(default=1)
    completion_percentage = models.IntegerField(default=0)

    # Resources
    assigned_crew = models.ForeignKey(
        Crew, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks"
    )
    assigned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="assigned_tasks"
    )
    cost_code = models.ForeignKey(
        "estimating.CostCode", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="tasks"
    )

    # Hours
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # Critical path
    is_critical_path = models.BooleanField(default=False)
    float_days = models.IntegerField(default=0)  # Total float (slack)
    early_start = models.DateField(null=True, blank=True)
    early_finish = models.DateField(null=True, blank=True)
    late_start = models.DateField(null=True, blank=True)
    late_finish = models.DateField(null=True, blank=True)

    # WBS / display
    sort_order = models.PositiveIntegerField(default=0)
    wbs_code = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        ordering = ["sort_order", "start_date"]
        indexes = [
            models.Index(fields=["project", "status"], name="sched_task_proj_status_idx"),
            models.Index(fields=["project", "is_critical_path"], name="sched_task_proj_cp_idx"),
        ]

    def __str__(self):
        return f"{self.wbs_code} {self.name}".strip()


class TaskDependency(models.Model):
    """Dependency relationship between two tasks."""

    class DependencyType(models.TextChoices):
        FINISH_TO_START = "finish_to_start", "Finish-to-Start (FS)"
        START_TO_START = "start_to_start", "Start-to-Start (SS)"
        FINISH_TO_FINISH = "finish_to_finish", "Finish-to-Finish (FF)"
        START_TO_FINISH = "start_to_finish", "Start-to-Finish (SF)"

    predecessor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="successor_deps")
    successor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="predecessor_deps")
    dependency_type = models.CharField(
        max_length=20, choices=DependencyType.choices, default=DependencyType.FINISH_TO_START
    )
    lag_days = models.IntegerField(default=0)

    class Meta:
        unique_together = [["predecessor", "successor"]]

    def __str__(self):
        return f"{self.predecessor.name} → {self.successor.name} ({self.dependency_type})"


class Equipment(TenantModel):
    """Equipment / asset management."""

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        IN_USE = "in_use", "In Use"
        MAINTENANCE = "maintenance", "Maintenance"
        RETIRED = "retired", "Retired"

    class DepreciationMethod(models.TextChoices):
        STRAIGHT_LINE = "straight_line", "Straight-Line"
        DECLINING_BALANCE = "declining_balance", "Declining Balance"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    equipment_type = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    current_project = models.ForeignKey(
        "projects.Project", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="equipment"
    )

    # Financials
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    depreciation_method = models.CharField(
        max_length=20, choices=DepreciationMethod.choices, default=DepreciationMethod.STRAIGHT_LINE
    )
    useful_life_years = models.IntegerField(default=5)
    salvage_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_book_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    daily_rental_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Maintenance
    next_maintenance = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["status"], name="sched_equipment_status_idx"),
        ]

    def __str__(self):
        return self.name

    def calculate_book_value(self):
        """Calculate current book value based on depreciation method."""
        if not self.purchase_date or not self.purchase_cost:
            return self.current_book_value
        from django.utils import timezone
        years_owned = (timezone.now().date() - self.purchase_date).days / 365.25
        cost = float(self.purchase_cost)
        salvage = float(self.salvage_value)
        if self.depreciation_method == self.DepreciationMethod.STRAIGHT_LINE:
            annual_dep = (cost - salvage) / max(self.useful_life_years, 1)
            book_value = max(cost - (annual_dep * years_owned), salvage)
        else:  # Declining balance
            rate = 2 / max(self.useful_life_years, 1)
            book_value = cost * ((1 - rate) ** years_owned)
            book_value = max(book_value, salvage)
        return round(book_value, 2)
