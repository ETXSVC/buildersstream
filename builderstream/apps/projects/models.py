"""Project Command Center and lifecycle models."""
import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TenantModel, TimeStampedModel


class Project(TenantModel):
    """Central project model — the command center."""

    class Status(models.TextChoices):
        LEAD = "lead", "Lead"
        PROSPECT = "prospect", "Prospect"
        ESTIMATE = "estimate", "Estimate"
        PROPOSAL = "proposal", "Proposal"
        CONTRACT = "contract", "Contract"
        PRODUCTION = "production", "Production"
        PUNCH_LIST = "punch_list", "Punch List"
        CLOSEOUT = "closeout", "Closeout"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"

    class ProjectType(models.TextChoices):
        RESIDENTIAL_REMODEL = "residential_remodel", "Residential Remodel"
        KITCHEN_BATH = "kitchen_bath", "Kitchen & Bath"
        ADDITION = "addition", "Addition"
        NEW_HOME = "new_home", "New Home"
        COMMERCIAL_BUILDOUT = "commercial_buildout", "Commercial Buildout"
        COMMERCIAL_RENOVATION = "commercial_renovation", "Commercial Renovation"
        ROOFING = "roofing", "Roofing"
        EXTERIOR = "exterior", "Exterior"
        SPECIALTY = "specialty", "Specialty"

    class HealthStatus(models.TextChoices):
        GREEN = "green", "Green"
        YELLOW = "yellow", "Yellow"
        RED = "red", "Red"

    # Identity
    name = models.CharField(max_length=255)
    project_number = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.LEAD
    )
    project_type = models.CharField(
        max_length=30, choices=ProjectType.choices, blank=True
    )

    # Client
    client = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )

    # Location
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    # Financial
    estimated_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    actual_revenue = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    estimated_cost = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    actual_cost = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    # Schedule
    start_date = models.DateField(null=True, blank=True)
    estimated_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)

    # Team
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_projects",
    )
    assigned_team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectTeamMember",
        related_name="team_projects",
        blank=True,
    )

    # Health
    health_score = models.PositiveSmallIntegerField(default=100)
    health_status = models.CharField(
        max_length=10,
        choices=HealthStatus.choices,
        default=HealthStatus.GREEN,
    )
    completion_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    # Metadata
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "project_type"]),
            models.Index(fields=["organization", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.project_number} - {self.name}"


class ProjectTeamMember(models.Model):
    """Through model for project team assignments."""

    class Role(models.TextChoices):
        PROJECT_MANAGER = "project_manager", "Project Manager"
        SUPERINTENDENT = "superintendent", "Superintendent"
        ESTIMATOR = "estimator", "Estimator"
        FOREMAN = "foreman", "Foreman"
        SUBCONTRACTOR = "subcontractor", "Subcontractor"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="team_members"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_assignments",
    )
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.OTHER
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["project", "user"]

    def __str__(self):
        return f"{self.user} - {self.project} ({self.get_role_display()})"


class ProjectStageTransition(TimeStampedModel):
    """Audit log for project status transitions."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="stage_transitions"
    )
    from_status = models.CharField(max_length=30, choices=Project.Status.choices)
    to_status = models.CharField(max_length=30, choices=Project.Status.choices)
    transitioned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="project_transitions",
    )
    notes = models.TextField(blank=True)
    requirements_met = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.project}: {self.from_status} -> {self.to_status}"


class ProjectMilestone(TenantModel):
    """Milestone tracking for projects."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="milestones"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    notify_client = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "due_date"]

    def __str__(self):
        return f"{self.project}: {self.name}"


class ActionItem(TimeStampedModel):
    """Organization-wide or project-specific action items."""

    class ItemType(models.TextChoices):
        TASK = "task", "Task"
        APPROVAL = "approval", "Approval"
        OVERDUE_INVOICE = "overdue_invoice", "Overdue Invoice"
        WEATHER_ALERT = "weather_alert", "Weather Alert"
        DEADLINE = "deadline", "Deadline"
        CLIENT_MESSAGE = "client_message", "Client Message"
        EXPIRING_BID = "expiring_bid", "Expiring Bid"
        INSPECTION_DUE = "inspection_due", "Inspection Due"

    class Priority(models.TextChoices):
        CRITICAL = "critical", "Critical"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="action_items",
        db_index=True,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="action_items",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_items",
    )
    due_date = models.DateField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    source_type = models.CharField(max_length=100, blank=True)
    source_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "is_resolved", "-created_at"]),
            models.Index(fields=["organization", "project", "is_resolved"]),
            models.Index(fields=["assigned_to", "is_resolved"]),
        ]

    def __str__(self):
        return self.title


class ActivityLog(TimeStampedModel):
    """Activity stream for organization and project events."""

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        STATUS_CHANGED = "status_changed", "Status Changed"
        UPLOADED = "uploaded", "Uploaded"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMMENTED = "commented", "Commented"
        CHECKED_IN = "checked_in", "Checked In"
        CHECKED_OUT = "checked_out", "Checked Out"

    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="activity_logs",
        db_index=True,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    entity_type = models.CharField(max_length=100, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["project", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user}: {self.action} on {self.entity_type}"


class DashboardLayout(TimeStampedModel):
    """Per-user dashboard widget layout configuration."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_layouts",
    )
    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="dashboard_layouts",
    )
    layout = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        unique_together = ["user", "organization"]

    def __str__(self):
        return f"Dashboard: {self.user} @ {self.organization}"
