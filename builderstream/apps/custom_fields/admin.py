from django.contrib import admin

from apps.custom_fields.models import CustomFieldDefinition, CustomFieldValue


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = [
        "label", "model_name", "field_type", "required", "is_active",
        "sort_order", "organization",
    ]
    list_filter = ["model_name", "field_type", "required", "is_active"]
    search_fields = ["label", "name"]
    ordering = ["model_name", "sort_order", "label"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = [
        (None, {
            "fields": ["organization", "model_name", "name", "label", "field_type"],
        }),
        ("Options", {
            "fields": ["options", "required", "default_value", "placeholder",
                       "help_text_field", "sort_order", "is_active"],
        }),
        ("Metadata", {
            "fields": ["id", "created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]


@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ["field", "content_type", "object_id", "value"]
    list_filter = ["content_type", "field__model_name"]
    search_fields = ["field__label", "field__name"]
    readonly_fields = ["id", "content_type", "object_id", "created_at", "updated_at"]
