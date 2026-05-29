"""Migration: update Project.status choices and remap legacy values.

Old flow: lead → prospect → estimate → proposal → contract →
          production → punch_list → closeout → completed (+ canceled)

New flow: prospect → site_survey → proposal → acceptance →
          in_progress → milestones → finish_project → billing →
          paid_complete (+ canceled)
"""
from django.db import migrations, models


# Map old status values → new status values.
# "lead" and "estimate" had no direct equivalent — map to closest stage.
STATUS_REMAP = {
    "lead": "prospect",
    "estimate": "proposal",
    "contract": "acceptance",
    "production": "in_progress",
    "punch_list": "milestones",
    "closeout": "finish_project",
    "completed": "paid_complete",
    # Values that exist in both old and new (unchanged):
    # "prospect", "proposal", "canceled" — no remapping needed
}


def remap_statuses_forward(apps, schema_editor):
    """Remap old status values to new ones."""
    Project = apps.get_model("projects", "Project")
    for old_val, new_val in STATUS_REMAP.items():
        Project.objects.filter(status=old_val).update(status=new_val)


def remap_statuses_backward(apps, schema_editor):
    """Reverse the remap (best-effort — some information is lost)."""
    Project = apps.get_model("projects", "Project")
    reverse_map = {v: k for k, v in STATUS_REMAP.items() if k not in ("lead",)}
    for new_val, old_val in reverse_map.items():
        Project.objects.filter(status=new_val).update(status=old_val)


class Migration(migrations.Migration):

    dependencies = [
        (
            "projects",
            "0003_rename_projects_ai_org_resolved_idx_projects_ac_organiz_c100fb_idx_and_more",
        ),
    ]

    operations = [
        # 1. Data migration: remap legacy stored values first
        migrations.RunPython(remap_statuses_forward, remap_statuses_backward),
        # 2. Update the field definition so Django knows the new choices
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[
                    ("prospect", "Prospect"),
                    ("site_survey", "Site Survey"),
                    ("proposal", "Proposal"),
                    ("acceptance", "Acceptance"),
                    ("in_progress", "In Progress"),
                    ("milestones", "Milestones"),
                    ("finish_project", "Finish Project"),
                    ("billing", "Billing"),
                    ("paid_complete", "Paid / Complete"),
                    ("canceled", "Canceled"),
                ],
                default="prospect",
                max_length=30,
            ),
        ),
    ]
