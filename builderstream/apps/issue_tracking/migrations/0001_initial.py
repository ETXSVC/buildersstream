"""Issue Tracking initial migration."""
import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
        ("projects", "0001_initial"),
        ("crm", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="IssueType",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("icon", models.CharField(blank=True, max_length=50)),
                ("color", models.CharField(default="#6366f1", max_length=7)),
                ("default_priority", models.CharField(
                    choices=[("critical", "Critical"), ("high", "High"), ("medium", "Medium"), ("low", "Low")],
                    default="medium",
                    max_length=20,
                )),
                ("sla_response_hours", models.PositiveIntegerField(default=4)),
                ("sla_resolution_hours", models.PositiveIntegerField(default=24)),
                ("is_active", models.BooleanField(default=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="issue_tracking_issuetype_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Issue",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("number", models.CharField(blank=True, max_length=20)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("priority", models.CharField(
                    choices=[("critical", "Critical"), ("high", "High"), ("medium", "Medium"), ("low", "Low")],
                    default="medium",
                    max_length=20,
                )),
                ("status", models.CharField(
                    choices=[
                        ("new", "New"), ("open", "Open"), ("in_progress", "In Progress"),
                        ("pending", "Pending"), ("resolved", "Resolved"), ("closed", "Closed"),
                    ],
                    default="new",
                    max_length=20,
                )),
                ("sla_response_due_at", models.DateTimeField(blank=True, null=True)),
                ("sla_resolution_due_at", models.DateTimeField(blank=True, null=True)),
                ("sla_response_met", models.BooleanField(blank=True, null=True)),
                ("sla_resolution_met", models.BooleanField(blank=True, null=True)),
                ("first_responded_at", models.DateTimeField(blank=True, null=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("custom_fields", models.JSONField(blank=True, default=dict)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="issue_tracking_issue_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("issue_type", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="issues",
                    to="issue_tracking.issuetype",
                )),
                ("project", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="issues",
                    to="projects.project",
                )),
                ("client", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="issues",
                    to="crm.contact",
                )),
                ("assignee", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="assigned_issues",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("reporter", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="reported_issues",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="IssueComment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("content", models.TextField()),
                ("is_edited", models.BooleanField(default=False)),
                ("edited_at", models.DateTimeField(blank=True, null=True)),
                ("is_internal", models.BooleanField(default=False)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="issue_tracking_issuecomment_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("issue", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="comments",
                    to="issue_tracking.issue",
                )),
                ("parent", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="replies",
                    to="issue_tracking.issuecomment",
                )),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="IssueAttachment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file_key", models.CharField(max_length=500)),
                ("filename", models.CharField(max_length=255)),
                ("file_size", models.PositiveIntegerField(default=0)),
                ("content_type", models.CharField(blank=True, max_length=100)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="issue_tracking_issueattachment_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("issue", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="attachments",
                    to="issue_tracking.issue",
                )),
                ("uploaded_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="issue_attachments",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.CreateModel(
            name="CannedResponse",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="issue_tracking_cannedresponse_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("issue_type", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="canned_responses",
                    to="issue_tracking.issuetype",
                )),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="EscalationRule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("trigger_condition", models.JSONField(default=dict)),
                ("action_type", models.CharField(
                    choices=[("reassign", "Reassign"), ("notify", "Send Notification"), ("change_priority", "Change Priority")],
                    max_length=30,
                )),
                ("action_config", models.JSONField(default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="issue_tracking_escalationrule_set",
                    to="tenants.organization",
                )),
                ("created_by", models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="+",
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={"ordering": ["name"]},
        ),
        # Indexes
        migrations.AddIndex(
            model_name="issuetype",
            index=models.Index(fields=["organization", "is_active"], name="it_issuetype_org_active_idx"),
        ),
        migrations.AddIndex(
            model_name="issue",
            index=models.Index(fields=["organization", "status"], name="it_issue_org_status_idx"),
        ),
        migrations.AddIndex(
            model_name="issue",
            index=models.Index(fields=["organization", "priority"], name="it_issue_org_priority_idx"),
        ),
        migrations.AddIndex(
            model_name="issue",
            index=models.Index(fields=["organization", "-created_at"], name="it_issue_org_created_idx"),
        ),
        migrations.AddIndex(
            model_name="issue",
            index=models.Index(fields=["assignee"], name="it_issue_assignee_idx"),
        ),
        migrations.AddIndex(
            model_name="issuecomment",
            index=models.Index(fields=["issue", "created_at"], name="it_comment_issue_created_idx"),
        ),
        migrations.AddIndex(
            model_name="issueattachment",
            index=models.Index(fields=["issue"], name="it_attachment_issue_idx"),
        ),
        migrations.AddIndex(
            model_name="cannedresponse",
            index=models.Index(fields=["organization", "is_active"], name="it_canned_org_active_idx"),
        ),
        migrations.AddIndex(
            model_name="escalationrule",
            index=models.Index(fields=["organization", "is_active"], name="it_escalation_org_active_idx"),
        ),
    ]
