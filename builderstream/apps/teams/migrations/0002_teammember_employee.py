"""Replace TeamMember.user (User FK) with TeamMember.employee (Employee FK)."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0001_initial"),
        ("payroll", "0001_initial"),
    ]

    operations = [
        # Drop existing rows (dev data only — safe to truncate)
        migrations.RunSQL("DELETE FROM teams_teammember;", reverse_sql=migrations.RunSQL.noop),

        # Remove old user FK and unique constraint
        migrations.AlterUniqueTogether(name="teammember", unique_together=set()),
        migrations.RemoveField(model_name="teammember", name="user"),

        # Add new employee FK
        migrations.AddField(
            model_name="teammember",
            name="employee",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="team_memberships",
                to="payroll.employee",
            ),
        ),

        # Restore unique constraint on (team, employee)
        migrations.AlterUniqueTogether(
            name="teammember",
            unique_together={("team", "employee")},
        ),
    ]
