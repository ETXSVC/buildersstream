"""Document management models: docs, photos, RFIs, submittals."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Folder(TenantModel):
    """Document folder structure."""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="folders")
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    def __str__(self):
        return self.name


class Document(TenantModel):
    """Project document."""

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="documents")
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name="documents")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/%Y/%m/")
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class RFI(TenantModel):
    """Request for Information."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ANSWERED = "answered", "Answered"
        CLOSED = "closed", "Closed"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="rfis")
    number = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    question = models.TextField()
    answer = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "RFI"
        verbose_name_plural = "RFIs"

    def __str__(self):
        return f"RFI #{self.number}: {self.subject}"


class Submittal(TenantModel):
    """Construction submittal tracking."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        RESUBMIT = "resubmit", "Resubmit Required"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="submittals")
    number = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    spec_section = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    submitted_date = models.DateField(null=True, blank=True)
    required_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Submittal #{self.number}: {self.title}"
