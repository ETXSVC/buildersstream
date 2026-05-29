import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomFieldDefinition",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)ss",
                        to="tenants.organization",
                    ),
                ),
                (
                    "model_name",
                    models.CharField(
                        choices=[
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
                        ],
                        db_index=True,
                        max_length=50,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("label", models.CharField(max_length=200)),
                (
                    "field_type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("textarea", "Text Area"),
                            ("number", "Number"),
                            ("date", "Date"),
                            ("boolean", "Yes / No"),
                            ("select", "Single Select"),
                            ("multi_select", "Multi Select"),
                            ("url", "URL"),
                            ("email", "Email"),
                            ("phone", "Phone"),
                        ],
                        default="text",
                        max_length=20,
                    ),
                ),
                ("options", models.JSONField(blank=True, default=list)),
                ("required", models.BooleanField(default=False)),
                ("default_value", models.JSONField(blank=True, null=True)),
                ("placeholder", models.CharField(blank=True, default="", max_length=200)),
                (
                    "help_text_field",
                    models.CharField(
                        blank=True, db_column="help_text", default="", max_length=500
                    ),
                ),
                ("sort_order", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Custom Field Definition",
                "verbose_name_plural": "Custom Field Definitions",
                "ordering": ["model_name", "sort_order", "label"],
            },
        ),
        migrations.CreateModel(
            name="CustomFieldValue",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="values",
                        to="custom_fields.customfielddefinition",
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                ("object_id", models.UUIDField(db_index=True)),
                ("value", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Custom Field Value",
                "verbose_name_plural": "Custom Field Values",
            },
        ),
        migrations.AddConstraint(
            model_name="customfielddefinition",
            constraint=models.UniqueConstraint(
                fields=["organization", "model_name", "name"],
                name="unique_cf_def_org_model_name",
            ),
        ),
        migrations.AddConstraint(
            model_name="customfieldvalue",
            constraint=models.UniqueConstraint(
                fields=["field", "content_type", "object_id"],
                name="unique_cf_val_field_ct_obj",
            ),
        ),
        migrations.AddIndex(
            model_name="customfielddefinition",
            index=models.Index(
                fields=["organization", "model_name"], name="cf_def_org_model"
            ),
        ),
        migrations.AddIndex(
            model_name="customfielddefinition",
            index=models.Index(
                fields=["organization", "is_active"], name="cf_def_org_active"
            ),
        ),
        migrations.AddIndex(
            model_name="customfieldvalue",
            index=models.Index(
                fields=["content_type", "object_id"], name="cf_val_ct_obj"
            ),
        ),
    ]
