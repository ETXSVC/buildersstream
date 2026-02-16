"""Financial models: job costing, invoicing, accounting, change orders."""
from django.db import models

from apps.core.models import TenantModel


class Budget(TenantModel):
    """Project budget tracking."""

    project = models.OneToOneField("projects.Project", on_delete=models.CASCADE, related_name="budget")
    original_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    revised_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    committed_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"Budget: {self.project}"


class Invoice(TenantModel):
    """Client invoice."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        VOID = "void", "Void"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class ChangeOrder(TenantModel):
    """Project change order."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="change_orders")
    number = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    submitted_date = models.DateField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"CO #{self.number} - {self.title}"
