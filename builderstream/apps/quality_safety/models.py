"""Quality and safety models: inspections, safety, OSHA compliance."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Inspection(TenantModel):
    """Quality inspection record."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        CORRECTIVE_ACTION = "corrective_action", "Corrective Action Required"

    class InspectionType(models.TextChoices):
        QUALITY = "quality", "Quality"
        SAFETY = "safety", "Safety"
        CODE = "code", "Code Compliance"
        ENVIRONMENTAL = "environmental", "Environmental"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="inspections")
    inspection_type = models.CharField(max_length=20, choices=InspectionType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    findings = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class SafetyIncident(TenantModel):
    """Safety incident report."""

    class Severity(models.TextChoices):
        NEAR_MISS = "near_miss", "Near Miss"
        MINOR = "minor", "Minor"
        MODERATE = "moderate", "Moderate"
        SERIOUS = "serious", "Serious"
        CRITICAL = "critical", "Critical"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="safety_incidents")
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices)
    incident_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    corrective_actions = models.TextField(blank=True)
    is_osha_recordable = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"


class SafetyChecklist(TenantModel):
    """Reusable safety checklist template."""

    name = models.CharField(max_length=255)
    items = models.JSONField(default=list)
    is_template = models.BooleanField(default=True)

    def __str__(self):
        return self.name
