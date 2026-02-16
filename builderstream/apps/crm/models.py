"""CRM models: leads, pipeline, contacts, marketing."""
from django.db import models

from apps.core.models import TenantModel


class Contact(TenantModel):
    """Contact/lead in the CRM system."""

    class ContactType(models.TextChoices):
        LEAD = "lead", "Lead"
        PROSPECT = "prospect", "Prospect"
        CLIENT = "client", "Client"
        SUBCONTRACTOR = "subcontractor", "Subcontractor"
        VENDOR = "vendor", "Vendor"

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    contact_type = models.CharField(max_length=20, choices=ContactType.choices, default=ContactType.LEAD)
    source = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PipelineStage(TenantModel):
    """Configurable pipeline stages."""

    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#3B82F6")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Deal(TenantModel):
    """Sales deal/opportunity in the pipeline."""

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="deals")
    stage = models.ForeignKey(PipelineStage, on_delete=models.PROTECT, related_name="deals")
    title = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    probability = models.PositiveIntegerField(default=50)
    expected_close = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title
