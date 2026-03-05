import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("action", models.CharField(
                    choices=[
                        ("login", "Login"),
                        ("login_failed", "Login Failed"),
                        ("logout", "Logout"),
                        ("password_changed", "Password Changed"),
                        ("2fa_enabled", "2FA Enabled"),
                        ("2fa_disabled", "2FA Disabled"),
                        ("2fa_failed", "2FA Code Failed"),
                        ("user_created", "User Created"),
                        ("user_updated", "User Updated"),
                        ("user_deleted", "User Deleted"),
                        ("org_settings_changed", "Org Settings Changed"),
                        ("member_invited", "Member Invited"),
                        ("member_removed", "Member Removed"),
                        ("role_changed", "Role Changed"),
                        ("export", "Data Export"),
                        ("api_key_created", "API Key Created"),
                        ("api_key_revoked", "API Key Revoked"),
                        ("permission_denied", "Permission Denied"),
                    ],
                    max_length=50,
                )),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("path", models.CharField(blank=True, max_length=500)),
                ("user", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="audit_logs",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("org", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="audit_logs",
                    to="tenants.organization",
                )),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="IPWhitelist",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("cidr", models.CharField(max_length=50)),
                ("label", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("org", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="ip_whitelist",
                    to="tenants.organization",
                )),
                ("added_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["org", "cidr"]},
        ),
        migrations.CreateModel(
            name="UserSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("jti", models.CharField(db_index=True, max_length=255, unique=True)),
                ("device_name", models.CharField(blank=True, max_length=200)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("last_active", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="sessions",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-last_active"]},
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["org", "-created_at"], name="auditlog_org_created_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["user", "-created_at"], name="auditlog_user_created_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["action", "-created_at"], name="auditlog_action_created_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["ip_address", "-created_at"], name="auditlog_ip_created_idx"),
        ),
        migrations.AddIndex(
            model_name="ipwhitelist",
            index=models.Index(fields=["org", "is_active"], name="ipwhitelist_org_active_idx"),
        ),
        migrations.AddIndex(
            model_name="usersession",
            index=models.Index(fields=["user", "is_active"], name="usersession_user_active_idx"),
        ),
    ]
