"""Core abstract models for the BuilderStream platform."""
import uuid

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TenantManager(models.Manager):
    """Manager that auto-filters querysets by organization."""

    def for_organization(self, organization):
        return self.get_queryset().filter(organization=organization)


class TenantModel(TimeStampedModel):
    """Abstract base model for multi-tenant resources.

    Extends TimeStampedModel with an organization FK and
    a custom manager that supports organization-scoped filtering.
    """

    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )

    objects = TenantManager()

    class Meta:
        abstract = True
