import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganizationBranding",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="branding",
                    to="tenants.organization",
                )),
                ("logo", models.ImageField(blank=True, null=True, upload_to="branding/logos/")),
                ("favicon", models.ImageField(blank=True, null=True, upload_to="branding/favicons/")),
                ("company_name_override", models.CharField(blank=True, max_length=200)),
                ("primary_color", models.CharField(default="#f59e0b", max_length=20)),
                ("primary_dark", models.CharField(default="#d97706", max_length=20)),
                ("accent_color", models.CharField(default="#1e293b", max_length=20)),
                ("sidebar_bg", models.CharField(default="#0f172a", max_length=20)),
                ("sidebar_text", models.CharField(default="#f8fafc", max_length=20)),
                ("font_family", models.CharField(default="Inter, sans-serif", max_length=100)),
                ("custom_css", models.TextField(blank=True)),
                ("support_email", models.EmailField(blank=True)),
                ("support_phone", models.CharField(blank=True, max_length=30)),
                ("portal_welcome_message", models.TextField(blank=True)),
            ],
            options={"verbose_name": "Organization Branding", "verbose_name_plural": "Organization Branding"},
        ),
    ]
