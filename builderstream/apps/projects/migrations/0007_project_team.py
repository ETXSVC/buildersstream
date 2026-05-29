import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0006_projectcomment_created_by_and_more"),
        ("teams", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="team",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="projects",
                to="teams.team",
            ),
        ),
    ]
