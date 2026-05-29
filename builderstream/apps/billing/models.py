"""Stripe billing models — audit log and invoice sync."""
from django.db import models

from apps.core.models import TimeStampedModel


class SubscriptionEvent(TimeStampedModel):
    """Audit log for Stripe subscription lifecycle events.

    Every incoming Stripe webhook creates one of these records so we have
    a full, immutable history of billing activity per organization.
    """

    class EventType(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        CANCELED = "canceled", "Canceled"
        PAYMENT_SUCCEEDED = "payment_succeeded", "Payment Succeeded"
        PAYMENT_FAILED = "payment_failed", "Payment Failed"
        TRIAL_ENDING = "trial_ending", "Trial Ending"
        TRIAL_ENDED = "trial_ended", "Trial Ended"

    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="subscription_events",
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    stripe_event_id = models.CharField(max_length=255, unique=True)
    data = models.JSONField(default=dict, help_text="Raw Stripe event payload")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self):
        return f"{self.organization} — {self.get_event_type_display()} ({self.stripe_event_id})"


class Invoice(TimeStampedModel):
    """Invoice record synced from Stripe.

    Created/updated via the ``invoice.payment_succeeded`` and
    ``invoice.payment_failed`` webhook events.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        PAID = "paid", "Paid"
        VOID = "void", "Void"
        UNCOLLECTIBLE = "uncollectible", "Uncollectible"

    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    stripe_invoice_id = models.CharField(max_length=255, unique=True)
    amount_due = models.IntegerField(help_text="Amount due in cents")
    amount_paid = models.IntegerField(default=0, help_text="Amount paid in cents")
    currency = models.CharField(max_length=3, default="usd")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)
    hosted_invoice_url = models.URLField(max_length=500, blank=True)
    pdf_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.organization} — ${self.amount_due / 100:.2f} ({self.get_status_display()})"
