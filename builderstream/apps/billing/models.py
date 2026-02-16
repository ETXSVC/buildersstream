"""Stripe billing, subscriptions, and module activation."""
from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Plan(TimeStampedModel):
    """Subscription plan definition."""

    name = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=255, unique=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_users = models.PositiveIntegerField(default=5)
    max_projects = models.PositiveIntegerField(default=10)
    features = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(TimeStampedModel):
    """Organization subscription to a plan."""

    organization = models.OneToOneField(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    stripe_subscription_id = models.CharField(max_length=255, unique=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default="active")
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.organization} - {self.plan}"
