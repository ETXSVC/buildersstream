from rest_framework import serializers

from apps.custom_fields.models import CustomFieldDefinition, CustomFieldValue


class CustomFieldDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFieldDefinition
        fields = [
            "id",
            "model_name",
            "name",
            "label",
            "field_type",
            "options",
            "required",
            "default_value",
            "placeholder",
            "help_text_field",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        import re

        if not re.match(r"^[a-z][a-z0-9_]*$", value):
            raise serializers.ValidationError(
                "Name must start with a letter and contain only lowercase letters, "
                "numbers, and underscores."
            )
        return value

    def validate(self, attrs):
        ft = attrs.get("field_type", "")
        options = attrs.get("options", [])
        if ft in ("select", "multi_select") and not options:
            raise serializers.ValidationError(
                {"options": "Options are required for select and multi_select fields."}
            )
        return attrs


class CustomFieldDefinitionListSerializer(serializers.ModelSerializer):
    """Compact serializer for list views."""

    class Meta:
        model = CustomFieldDefinition
        fields = [
            "id",
            "model_name",
            "name",
            "label",
            "field_type",
            "required",
            "is_active",
            "sort_order",
        ]
        read_only_fields = fields


class CustomFieldValueSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source="field.name", read_only=True)
    field_label = serializers.CharField(source="field.label", read_only=True)
    field_type = serializers.CharField(source="field.field_type", read_only=True)

    class Meta:
        model = CustomFieldValue
        fields = ["id", "field", "field_name", "field_label", "field_type", "value"]
        read_only_fields = ["id", "field_name", "field_label", "field_type"]
