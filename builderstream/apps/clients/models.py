"""Client portal models: approvals, selections."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class ClientPortalAccess(TenantModel):
    """Client access to project portal."""

    client_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portal_access")
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="client_access")
    can_view_documents = models.BooleanField(default=True)
    can_view_schedule = models.BooleanField(default=True)
    can_view_financials = models.BooleanField(default=False)
    can_approve_selections = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["client_user", "project"]

    def __str__(self):
        return f"{self.client_user} - {self.project}"


class Selection(TenantModel):
    """Client selection/approval item."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REVISED = "revised", "Revised"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="selections")
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    options = models.JSONField(default=list, blank=True)
    selected_option = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.category}: {self.title}"
