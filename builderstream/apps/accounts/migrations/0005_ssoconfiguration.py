"""Migration: Add SSOConfiguration model for SAML 2.0 Enterprise SSO."""
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_remove_notification_preferences_jsonfield"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SSOConfiguration",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="sso_configurations",
                    to="tenants.organization",
                )),
                ("idp_entity_id", models.CharField(blank=True, help_text="IdP EntityID (issuer)", max_length=500)),
                ("idp_sso_url", models.URLField(blank=True, help_text="IdP Single Sign-On URL", max_length=500)),
                ("idp_slo_url", models.URLField(blank=True, help_text="IdP Single Logout URL", max_length=500)),
                ("idp_x509_cert", models.TextField(blank=True, help_text="IdP X.509 certificate (PEM, no headers)")),
                ("is_enabled", models.BooleanField(default=False)),
                ("auto_provision", models.BooleanField(
                    default=True,
                    help_text="Automatically create user accounts on first SSO login",
                )),
                ("default_role", models.CharField(default="read_only", max_length=20)),
                ("attr_email", models.CharField(default="email", max_length=200)),
                ("attr_first_name", models.CharField(default="firstName", max_length=200)),
                ("attr_last_name", models.CharField(default="lastName", max_length=200)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
