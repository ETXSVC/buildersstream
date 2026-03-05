import django.db.models.deletion
import uuid
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
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="notifications_notification_set",
                    to="tenants.organization",
                    db_index=True,
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="notifications_notification_created",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("recipient", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="notifications",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("notification_type", models.CharField(
                    choices=[
                        ("project_status_changed", "Project Status Changed"),
                        ("project_health_alert", "Project Health Alert"),
                        ("action_item_assigned", "Action Item Assigned"),
                        ("action_item_due", "Action Item Due"),
                        ("rfi_submitted", "RFI Submitted"),
                        ("rfi_response", "RFI Response"),
                        ("submittal_response", "Submittal Response"),
                        ("document_uploaded", "Document Uploaded"),
                        ("invoice_sent", "Invoice Sent"),
                        ("invoice_paid", "Invoice Paid"),
                        ("change_order_submitted", "Change Order Submitted"),
                        ("change_order_approved", "Change Order Approved"),
                        ("daily_log_submitted", "Daily Log Submitted"),
                        ("clock_in", "Clock In"),
                        ("incident_reported", "Incident Reported"),
                        ("inspection_due", "Inspection Due"),
                        ("proposal_viewed", "Proposal Viewed"),
                        ("proposal_signed", "Proposal Signed"),
                        ("lead_assigned", "Lead Assigned"),
                        ("service_ticket_created", "Service Ticket Created"),
                        ("service_ticket_updated", "Service Ticket Updated"),
                        ("mention", "Mention"),
                        ("system", "System"),
                    ],
                    default="system",
                    max_length=50,
                )),
                ("priority", models.CharField(
                    choices=[("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
                    default="normal",
                    max_length=10,
                )),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField(blank=True)),
                ("data", models.JSONField(blank=True, default=dict)),
                ("is_read", models.BooleanField(default=False)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="NotificationPreference",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="notifications_notificationpreference_set",
                    to="tenants.organization",
                    db_index=True,
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="notifications_notificationpreference_created",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("user", models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="notification_preferences",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("in_app_enabled", models.BooleanField(default=True)),
                ("email_enabled", models.BooleanField(default=True)),
                ("push_enabled", models.BooleanField(default=False)),
                ("quiet_hours_start", models.TimeField(blank=True, null=True)),
                ("quiet_hours_end", models.TimeField(blank=True, null=True)),
                ("type_overrides", models.JSONField(blank=True, default=dict)),
            ],
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["organization", "recipient", "-created_at"], name="notif_org_recip_idx"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["organization", "recipient", "is_read"], name="notif_org_recip_read_idx"),
        ),
        migrations.AddIndex(
            model_name="notificationpreference",
            index=models.Index(fields=["organization", "user"], name="notifpref_org_user_idx"),
        ),
    ]
