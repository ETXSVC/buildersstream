"""Estimating models: takeoffs, cost database, proposals."""
from django.db import models

from apps.core.models import TenantModel


class CostCode(TenantModel):
    """Standard cost code for estimating."""

    code = models.CharField(max_length=20)
    description = models.CharField(max_length=255)
    unit = models.CharField(max_length=20, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.description}"


class Estimate(TenantModel):
    """Project estimate/takeoff."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEW = "review", "In Review"
        APPROVED = "approved", "Approved"
        SENT = "sent", "Sent to Client"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="estimates")
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class EstimateLineItem(TenantModel):
    """Individual line item in an estimate."""

    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name="line_items")
    cost_code = models.ForeignKey(CostCode, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    unit = models.CharField(max_length=20, blank=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description
