"""Custom Fields Engine — org-scoped field definitions and values."""
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import TenantModel


class CustomFieldDefinition(TenantModel):
    """Org-scoped custom field definition for a named model.

    ``model_name`` is the snake_case model identifier used by the frontend
    and the CustomFieldsMixin (e.g. "project", "lead", "contact").  Values
    are intentionally stored as strings so no migration is needed when the
    available model list changes.
    """

    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        TEXTAREA = "textarea", "Text Area"
        NUMBER = "number", "Number"
        DATE = "date", "Date"
        BOOLEAN = "boolean", "Yes / No"
        SELECT = "select", "Single Select"
        MULTI_SELECT = "multi_select", "Multi Select"
        URL = "url", "URL"
        EMAIL = "email", "Email"
        PHONE = "phone", "Phone"

    MODEL_CHOICES = [
        ("project", "Project"),
        ("lead", "Lead"),
        ("contact", "Contact"),
        ("company", "Company"),
        ("invoice", "Invoice"),
        ("estimate", "Estimate"),
        ("proposal", "Proposal"),
        ("service_ticket", "Service Ticket"),
        ("inspection", "Inspection"),
        ("daily_log", "Daily Log"),
    ]

    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES, db_index=True)
    name = models.CharField(
        max_length=100,
        help_text="Internal identifier (letters, numbers, underscores only).",
    )
    label = models.CharField(max_length=200)
    field_type = models.CharField(
        max_length=20, choices=FieldType.choices, default=FieldType.TEXT
    )
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="List of option strings for select / multi_select fields.",
    )
    required = models.BooleanField(default=False)
    default_value = models.JSONField(null=True, blank=True)
    placeholder = models.CharField(max_length=200, blank=True, default="")
    help_text_field = models.CharField(
        max_length=500, blank=True, default="", db_column="help_text"
    )
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("organization", "model_name", "name")]
        ordering = ["model_name", "sort_order", "label"]
        indexes = [
            models.Index(fields=["organization", "model_name"], name="cf_def_org_model"),
            models.Index(fields=["organization", "is_active"], name="cf_def_org_active"),
        ]
        verbose_name = "Custom Field Definition"
        verbose_name_plural = "Custom Field Definitions"

    def __str__(self):
        return f"{self.model_name}.{self.name} ({self.get_field_type_display()})"


class CustomFieldValue(models.Model):
    """Value storage for a custom field on any object.

    Uses Django's GenericForeignKey so a single table stores values for any
    model.  The ``field`` FK points back to the definition so all metadata
    (label, type, options) lives in one place.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(
        CustomFieldDefinition,
        on_delete=models.CASCADE,
        related_name="values",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    value = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("field", "content_type", "object_id")]
        indexes = [
            models.Index(
                fields=["content_type", "object_id"], name="cf_val_ct_obj"
            ),
        ]
        verbose_name = "Custom Field Value"
        verbose_name_plural = "Custom Field Values"

    def __str__(self):
        return f"{self.field.label}: {self.value}"
