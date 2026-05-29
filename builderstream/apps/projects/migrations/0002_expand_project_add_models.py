"""Expand Project model and add ProjectTeamMember, ProjectStageTransition,
ProjectMilestone, ActionItem, ActivityLog, DashboardLayout models.

Renames: number -> project_number, contract_amount -> estimated_value
Data migration: maps old status/type values to new enum values
"""
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_status_and_type(apps, schema_editor):
    """Map old status/type choices to new values and backfill project_number."""
    Project = apps.get_model("projects", "Project")

    STATUS_MAP = {
        "bid": "estimate",
        "awarded": "contract",
        "in_progress": "production",
        "on_hold": "production",
        "closed": "closeout",
        # "lead" and "completed" stay the same
    }
    TYPE_MAP = {
        "residential": "residential_remodel",
        "commercial": "commercial_buildout",
        "industrial": "commercial_buildout",
        "infrastructure": "specialty",
        "renovation": "commercial_renovation",
    }

    for project in Project.objects.all():
        changed = False

        new_status = STATUS_MAP.get(project.status)
        if new_status:
            project.status = new_status
            changed = True

        new_type = TYPE_MAP.get(project.project_type)
        if new_type:
            project.project_type = new_type
            changed = True

        # Backfill project_number from old number field or generate a legacy one
        if not project.project_number:
            project.project_number = f"BSP-LEGACY-{str(project.pk)[:8]}"
            changed = True

        if changed:
            project.save(update_fields=["status", "project_type", "project_number"])


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
        ("crm", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Phase 1: Rename fields ──────────────────────────────
        migrations.RenameField(
            model_name="project",
            old_name="number",
            new_name="project_number",
        ),
        migrations.RenameField(
            model_name="project",
            old_name="contract_amount",
            new_name="estimated_value",
        ),

        # ── Phase 2: Add new fields to Project ──────────────────
        migrations.AddField(
            model_name="project",
            name="client",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="projects",
                to="crm.contact",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="latitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="longitude",
            field=models.DecimalField(
                blank=True, decimal_places=6, max_digits=9, null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="actual_revenue",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=14, null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="estimated_cost",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=14, null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="actual_cost",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=14, null=True,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="project_manager",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="managed_projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="health_score",
            field=models.PositiveSmallIntegerField(default=100),
        ),
        migrations.AddField(
            model_name="project",
            name="health_status",
            field=models.CharField(
                choices=[("green", "Green"), ("yellow", "Yellow"), ("red", "Red")],
                default="green",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="completion_percentage",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name="project",
            name="tags",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="project",
            name="custom_fields",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="project",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),

        # ── Phase 3: Alter existing fields (choices, max_length) ─
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[
                    ("lead", "Lead"), ("prospect", "Prospect"),
                    ("estimate", "Estimate"), ("proposal", "Proposal"),
                    ("contract", "Contract"), ("production", "Production"),
                    ("punch_list", "Punch List"), ("closeout", "Closeout"),
                    ("completed", "Completed"), ("canceled", "Canceled"),
                ],
                default="lead",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="project_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("residential_remodel", "Residential Remodel"),
                    ("kitchen_bath", "Kitchen & Bath"),
                    ("addition", "Addition"),
                    ("new_home", "New Home"),
                    ("commercial_buildout", "Commercial Buildout"),
                    ("commercial_renovation", "Commercial Renovation"),
                    ("roofing", "Roofing"),
                    ("exterior", "Exterior"),
                    ("specialty", "Specialty"),
                ],
                max_length=30,
            ),
        ),

        # ── Phase 4: Data migration ─────────────────────────────
        migrations.RunPython(
            migrate_status_and_type,
            migrations.RunPython.noop,
        ),

        # ── Phase 5: Make project_number unique ──────────────────
        migrations.AlterField(
            model_name="project",
            name="project_number",
            field=models.CharField(db_index=True, max_length=50, unique=True),
        ),

        # ── Phase 6: Add indexes to Project ──────────────────────
        migrations.AddIndex(
            model_name="project",
            index=models.Index(
                fields=["organization", "status"],
                name="projects_pr_organiz_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(
                fields=["organization", "project_type"],
                name="projects_pr_organiz_type_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(
                fields=["organization", "-created_at"],
                name="projects_pr_organiz_created_idx",
            ),
        ),

        # ── Phase 7: Create new models ──────────────────────────
        migrations.CreateModel(
            name="ProjectTeamMember",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("role", models.CharField(choices=[
                    ("project_manager", "Project Manager"),
                    ("superintendent", "Superintendent"),
                    ("estimator", "Estimator"),
                    ("foreman", "Foreman"),
                    ("subcontractor", "Subcontractor"),
                    ("other", "Other"),
                ], default="other", max_length=20)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="team_members", to="projects.project")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="project_assignments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("project", "user")},
            },
        ),

        # Add M2M through field to Project
        migrations.AddField(
            model_name="project",
            name="assigned_team",
            field=models.ManyToManyField(
                blank=True,
                related_name="team_projects",
                through="projects.ProjectTeamMember",
                to=settings.AUTH_USER_MODEL,
            ),
        ),

        migrations.CreateModel(
            name="ProjectStageTransition",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("from_status", models.CharField(choices=[
                    ("lead", "Lead"), ("prospect", "Prospect"),
                    ("estimate", "Estimate"), ("proposal", "Proposal"),
                    ("contract", "Contract"), ("production", "Production"),
                    ("punch_list", "Punch List"), ("closeout", "Closeout"),
                    ("completed", "Completed"), ("canceled", "Canceled"),
                ], max_length=30)),
                ("to_status", models.CharField(choices=[
                    ("lead", "Lead"), ("prospect", "Prospect"),
                    ("estimate", "Estimate"), ("proposal", "Proposal"),
                    ("contract", "Contract"), ("production", "Production"),
                    ("punch_list", "Punch List"), ("closeout", "Closeout"),
                    ("completed", "Completed"), ("canceled", "Canceled"),
                ], max_length=30)),
                ("notes", models.TextField(blank=True)),
                ("requirements_met", models.JSONField(blank=True, default=dict)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stage_transitions", to="projects.project")),
                ("transitioned_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="project_transitions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["project", "-created_at"], name="projects_tr_proj_created_idx"),
                ],
            },
        ),

        migrations.CreateModel(
            name="ProjectMilestone",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("completed_date", models.DateField(blank=True, null=True)),
                ("is_completed", models.BooleanField(default=False)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("notify_client", models.BooleanField(default=False)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="milestones", to="projects.project")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(app_label)s_%(class)s_created", to=settings.AUTH_USER_MODEL)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="%(app_label)s_%(class)s_set", to="tenants.organization")),
            ],
            options={
                "ordering": ["sort_order", "due_date"],
            },
        ),

        migrations.CreateModel(
            name="ActionItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("item_type", models.CharField(choices=[
                    ("task", "Task"), ("approval", "Approval"),
                    ("overdue_invoice", "Overdue Invoice"),
                    ("weather_alert", "Weather Alert"),
                    ("deadline", "Deadline"),
                    ("client_message", "Client Message"),
                    ("expiring_bid", "Expiring Bid"),
                    ("inspection_due", "Inspection Due"),
                ], max_length=20)),
                ("priority", models.CharField(choices=[
                    ("critical", "Critical"), ("high", "High"),
                    ("medium", "Medium"), ("low", "Low"),
                ], default="medium", max_length=10)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("is_resolved", models.BooleanField(default=False)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("source_type", models.CharField(blank=True, max_length=100)),
                ("source_id", models.UUIDField(blank=True, null=True)),
                ("organization", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="action_items", to="tenants.organization")),
                ("project", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="action_items", to="projects.project")),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="action_items", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["organization", "is_resolved", "-created_at"], name="projects_ai_org_resolved_idx"),
                    models.Index(fields=["organization", "project", "is_resolved"], name="projects_ai_org_proj_res_idx"),
                    models.Index(fields=["assigned_to", "is_resolved"], name="projects_ai_assign_res_idx"),
                ],
            },
        ),

        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("action", models.CharField(choices=[
                    ("created", "Created"), ("updated", "Updated"),
                    ("status_changed", "Status Changed"),
                    ("uploaded", "Uploaded"), ("approved", "Approved"),
                    ("rejected", "Rejected"), ("commented", "Commented"),
                    ("checked_in", "Checked In"), ("checked_out", "Checked Out"),
                ], max_length=20)),
                ("entity_type", models.CharField(blank=True, max_length=100)),
                ("entity_id", models.UUIDField(blank=True, null=True)),
                ("description", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("organization", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="activity_logs", to="tenants.organization")),
                ("project", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="activity_logs", to="projects.project")),
                ("user", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="activity_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["organization", "-created_at"], name="projects_al_org_created_idx"),
                    models.Index(fields=["project", "-created_at"], name="projects_al_proj_created_idx"),
                    models.Index(fields=["user", "-created_at"], name="projects_al_user_created_idx"),
                ],
            },
        ),

        migrations.CreateModel(
            name="DashboardLayout",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("layout", models.JSONField(blank=True, default=dict)),
                ("is_default", models.BooleanField(default=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dashboard_layouts", to=settings.AUTH_USER_MODEL)),
                ("organization", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dashboard_layouts", to="tenants.organization")),
            ],
            options={
                "unique_together": {("user", "organization")},
            },
        ),
    ]
