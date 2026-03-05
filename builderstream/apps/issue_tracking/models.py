"""Issue Tracking models — issues, SLA, escalation, canned responses."""
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TenantModel


class IssueType(TenantModel):
    """Configurable issue type with SLA targets."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default="#6366f1")
    default_priority = models.CharField(
        max_length=20,
        default="medium",
        choices=[
            ("critical", "Critical"),
            ("high", "High"),
            ("medium", "Medium"),
            ("low", "Low"),
        ],
    )
    sla_response_hours = models.PositiveIntegerField(default=4)
    sla_resolution_hours = models.PositiveIntegerField(default=24)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "is_active"], name="it_issuetype_org_active_idx"),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Issue(TenantModel):
    """Core issue/ticket record."""

    class Priority(models.TextChoices):
        CRITICAL = "critical", "Critical"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    class Status(models.TextChoices):
        NEW = "new", "New"
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        PENDING = "pending", "Pending"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    # Auto-generated issue number per org
    number = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Classification
    issue_type = models.ForeignKey(
        IssueType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
    )
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    # Relations
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
    )
    client = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_issues",
    )

    # SLA tracking
    sla_response_due_at = models.DateTimeField(null=True, blank=True)
    sla_resolution_due_at = models.DateTimeField(null=True, blank=True)
    sla_response_met = models.BooleanField(null=True, blank=True)
    sla_resolution_met = models.BooleanField(null=True, blank=True)
    first_responded_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Extra metadata
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status"], name="it_issue_org_status_idx"),
            models.Index(fields=["organization", "priority"], name="it_issue_org_priority_idx"),
            models.Index(fields=["organization", "-created_at"], name="it_issue_org_created_idx"),
            models.Index(fields=["assignee"], name="it_issue_assignee_idx"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number} — {self.title}"

    @property
    def is_sla_response_breached(self):
        if self.sla_response_due_at and not self.first_responded_at:
            return timezone.now() > self.sla_response_due_at
        return False

    @property
    def is_sla_resolution_breached(self):
        if self.sla_resolution_due_at and self.status not in (
            Issue.Status.RESOLVED,
            Issue.Status.CLOSED,
        ):
            return timezone.now() > self.sla_resolution_due_at
        return False


class IssueComment(TenantModel):
    """Comment on an issue (threaded)."""

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_internal = models.BooleanField(default=False, help_text="Internal notes, not visible to clients")

    class Meta:
        indexes = [
            models.Index(fields=["issue", "created_at"], name="it_comment_issue_created_idx"),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.issue.number} by {self.created_by}"


class IssueAttachment(TenantModel):
    """File attachment on an issue."""

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="attachments")
    file_key = models.CharField(max_length=500)
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="issue_attachments",
    )

    class Meta:
        indexes = [
            models.Index(fields=["issue"], name="it_attachment_issue_idx"),
        ]

    def __str__(self):
        return self.filename


class CannedResponse(TenantModel):
    """Predefined response templates for common issues."""

    name = models.CharField(max_length=200)
    content = models.TextField()
    issue_type = models.ForeignKey(
        IssueType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="canned_responses",
        help_text="If set, only shown for this issue type",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "is_active"], name="it_canned_org_active_idx"),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name


class EscalationRule(TenantModel):
    """Rules to auto-escalate issues based on conditions."""

    class ActionType(models.TextChoices):
        REASSIGN = "reassign", "Reassign"
        NOTIFY = "notify", "Send Notification"
        CHANGE_PRIORITY = "change_priority", "Change Priority"

    name = models.CharField(max_length=200)
    trigger_condition = models.JSONField(
        default=dict,
        help_text=(
            "JSON: {condition_type: 'sla_breach'|'no_response'|'status_stale', "
            "hours_threshold: int, priority_filter: str}"
        ),
    )
    action_type = models.CharField(max_length=30, choices=ActionType.choices)
    action_config = models.JSONField(
        default=dict,
        help_text="JSON: {assignee_id: uuid} or {priority: str} or {user_ids: [uuid]}",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "is_active"], name="it_escalation_org_active_idx"),
        ]
        ordering = ["name"]

    def __str__(self):
        return self.name
