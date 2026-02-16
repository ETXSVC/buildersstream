"""Project Command Center and lifecycle models."""
from django.db import models

from apps.core.models import TenantModel


class Project(TenantModel):
    """Central project model - the command center."""

    class Status(models.TextChoices):
        LEAD = "lead", "Lead"
        BID = "bid", "Bid"
        AWARDED = "awarded", "Awarded"
        IN_PROGRESS = "in_progress", "In Progress"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"

    class ProjectType(models.TextChoices):
        RESIDENTIAL = "residential", "Residential"
        COMMERCIAL = "commercial", "Commercial"
        INDUSTRIAL = "industrial", "Industrial"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        RENOVATION = "renovation", "Renovation"

    name = models.CharField(max_length=255)
    number = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LEAD)
    project_type = models.CharField(max_length=20, choices=ProjectType.choices, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    contract_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    estimated_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.number} - {self.name}" if self.number else self.name
