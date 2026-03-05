"""Business logic for the Custom Fields Engine."""
from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType

from apps.custom_fields.models import CustomFieldDefinition, CustomFieldValue


class CustomFieldService:
    """CRUD and validation helpers for custom field definitions and values."""

    # ── Definitions ───────────────────────────────────────────────────────────

    @staticmethod
    def get_fields_for_model(org, model_name: str):
        """Return active field definitions for an org + model."""
        return (
            CustomFieldDefinition.objects.for_organization(org)
            .filter(model_name=model_name, is_active=True)
            .order_by("sort_order", "label")
        )

    # ── Values ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_values_for_object(obj) -> dict[str, Any]:
        """Return {field_name: value} dict for all custom fields on an object."""
        ct = ContentType.objects.get_for_model(obj)
        values = CustomFieldValue.objects.filter(
            content_type=ct, object_id=obj.pk
        ).select_related("field")
        return {cfv.field.name: cfv.value for cfv in values}

    @staticmethod
    def set_values_for_object(obj, field_values: dict[str, Any], org=None) -> None:
        """Bulk-upsert custom field values for an object.

        ``field_values`` is {field_name: value}.
        Unknown field names are silently ignored.
        """
        if not field_values:
            return

        ct = ContentType.objects.get_for_model(obj)

        # Resolve org: prefer explicit param, fall back to obj.organization
        if org is None and hasattr(obj, "organization"):
            org = obj.organization

        if org is None:
            return

        # Fetch matching definitions in one query
        definitions = {
            fd.name: fd
            for fd in CustomFieldDefinition.objects.for_organization(org).filter(
                name__in=field_values.keys(), is_active=True
            )
        }

        for field_name, value in field_values.items():
            fd = definitions.get(field_name)
            if fd is None:
                continue
            validated = CustomFieldService.validate_value(fd, value)
            CustomFieldValue.objects.update_or_create(
                field=fd,
                content_type=ct,
                object_id=obj.pk,
                defaults={"value": validated},
            )

    @staticmethod
    def validate_value(field_def: CustomFieldDefinition, value: Any) -> Any:
        """Validate and coerce value against the field definition.

        Returns the coerced value.  Raises ``ValueError`` on invalid input.
        """
        ft = field_def.field_type

        if value is None or value == "":
            if field_def.required:
                raise ValueError(f"Field '{field_def.label}' is required.")
            return None

        if ft == CustomFieldDefinition.FieldType.NUMBER:
            try:
                return float(value)
            except (TypeError, ValueError):
                raise ValueError(
                    f"Field '{field_def.label}' must be a number, got: {value!r}"
                )

        if ft == CustomFieldDefinition.FieldType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("1", "true", "yes")
            return bool(value)

        if ft == CustomFieldDefinition.FieldType.SELECT:
            if field_def.options and value not in field_def.options:
                raise ValueError(
                    f"'{value}' is not a valid option for '{field_def.label}'. "
                    f"Valid: {field_def.options}"
                )
            return value

        if ft == CustomFieldDefinition.FieldType.MULTI_SELECT:
            if not isinstance(value, list):
                value = [value]
            if field_def.options:
                invalid = [v for v in value if v not in field_def.options]
                if invalid:
                    raise ValueError(
                        f"Invalid options for '{field_def.label}': {invalid}"
                    )
            return value

        # text, textarea, date, url, email, phone — keep as string
        return str(value)

    @staticmethod
    def delete_values_for_object(obj) -> int:
        """Delete all custom field values for an object. Returns count deleted."""
        ct = ContentType.objects.get_for_model(obj)
        count, _ = CustomFieldValue.objects.filter(
            content_type=ct, object_id=obj.pk
        ).delete()
        return count
