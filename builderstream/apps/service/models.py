"""Service models: tickets, warranty, maintenance."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class ServiceTicket(TenantModel):
    """Service/warranty ticket."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING = "waiting", "Waiting on Client"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="service_tickets", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    contact_name = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    def __str__(self):
        return self.title


class WarrantyItem(TenantModel):
    """Warranty tracking for completed projects."""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="warranty_items")
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    warranty_start = models.DateField()
    warranty_end = models.DateField()
    manufacturer = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to="warranties/", blank=True)

    def __str__(self):
        return f"{self.item_name} - {self.project}"
