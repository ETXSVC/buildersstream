"""
Analytics v2: add widget_config to Dashboard, last_run fields to Report,
trend/variance_percent to KPI, and add indexes.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0002_initial"),
    ]

    operations = [
        # Dashboard: add widget_config
        migrations.AddField(
            model_name="dashboard",
            name="widget_config",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterModelOptions(
            name="dashboard",
            options={"ordering": ["-is_default", "name"]},
        ),
        migrations.AddIndex(
            model_name="dashboard",
            index=models.Index(
                fields=["organization", "is_default"],
                name="analytics_dash_org_default_idx",
            ),
        ),

        # Report: add last_run_at, last_run_result, SERVICE type, indexes
        migrations.AddField(
            model_name="report",
            name="last_run_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="report",
            name="last_run_result",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="report",
            name="report_type",
            field=models.CharField(
                choices=[
                    ("financial", "Financial"),
                    ("project", "Project"),
                    ("labor", "Labor"),
                    ("safety", "Safety"),
                    ("service", "Service"),
                    ("custom", "Custom"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="report",
            options={"ordering": ["name"]},
        ),
        migrations.AddIndex(
            model_name="report",
            index=models.Index(
                fields=["organization", "report_type"],
                name="analytics_rpt_org_type_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="report",
            index=models.Index(
                fields=["organization", "is_active"],
                name="analytics_rpt_org_active_idx",
            ),
        ),

        # KPI: add trend, variance_percent, SERVICE category, indexes
        migrations.AddField(
            model_name="kpi",
            name="trend",
            field=models.CharField(
                choices=[("up", "Up"), ("down", "Down"), ("stable", "Stable")],
                default="stable",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="kpi",
            name="variance_percent",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name="kpi",
            name="category",
            field=models.CharField(
                choices=[
                    ("financial", "Financial"),
                    ("project", "Project"),
                    ("labor", "Labor"),
                    ("safety", "Safety"),
                    ("service", "Service"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="kpi",
            options={
                "ordering": ["-period_end", "category", "name"],
                "verbose_name": "KPI",
                "verbose_name_plural": "KPIs",
            },
        ),
        migrations.AddIndex(
            model_name="kpi",
            index=models.Index(
                fields=["organization", "category"],
                name="analytics_kpi_org_cat_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="kpi",
            index=models.Index(
                fields=["organization", "-period_end"],
                name="analytics_kpi_org_period_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="kpi",
            index=models.Index(
                fields=["organization", "project"],
                name="analytics_kpi_org_proj_idx",
            ),
        ),
    ]
