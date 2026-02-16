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
    """Manager that auto-filters querysets by organization via thread-local context."""

    def get_queryset(self):
        qs = super().get_queryset()
        from apps.tenants.context import get_current_organization

        current_org = get_current_organization()
        if current_org is not None:
            qs = qs.filter(organization=current_org)
        return qs

    def for_organization(self, organization):
        """Explicit filter — bypasses thread-local and filters directly."""
        return super().get_queryset().filter(organization=organization)

    def unscoped(self):
        """Return queryset without tenant filtering (for admin/system use)."""
        return super().get_queryset()


class TenantModel(TimeStampedModel):
    """Abstract base model for multi-tenant resources.

    Extends TimeStampedModel with an organization FK and
    a custom manager that auto-filters by the current organization
    from thread-local storage.
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

    def save(self, *args, **kwargs):
        """Auto-set organization from thread-local if not already set."""
        if not self.organization_id:
            from apps.tenants.context import get_current_organization

            current_org = get_current_organization()
            if current_org is not None:
                self.organization = current_org
        super().save(*args, **kwargs)
