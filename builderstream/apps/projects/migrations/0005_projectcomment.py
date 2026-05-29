import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_update_project_status_choices"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectComment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="%(app_label)s_%(class)s_set",
                    to="tenants.organization",
                )),
                ("project", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="comments",
                    to="projects.project",
                )),
                ("parent", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="replies",
                    to="projects.projectcomment",
                )),
                ("author", models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="project_comments",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("body", models.TextField()),
                ("is_edited", models.BooleanField(default=False)),
                ("edited_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
            ],
            options={"ordering": ["created_at"]},
        ),
        migrations.AddIndex(
            model_name="projectcomment",
            index=models.Index(fields=["project", "created_at"], name="proj_comment_proj_created_idx"),
        ),
        migrations.AddIndex(
            model_name="projectcomment",
            index=models.Index(fields=["parent", "created_at"], name="proj_cmnt_parent_created_idx"),
        ),
    ]
