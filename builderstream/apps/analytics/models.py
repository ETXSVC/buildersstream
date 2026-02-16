"""Analytics models: reporting engine, dashboards, KPIs."""
from django.db import models

from apps.core.models import TenantModel


class Dashboard(TenantModel):
    """Custom dashboard configuration."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    layout = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Report(TenantModel):
    """Saved report definition."""

    class ReportType(models.TextChoices):
        FINANCIAL = "financial", "Financial"
        PROJECT = "project", "Project"
        LABOR = "labor", "Labor"
        SAFETY = "safety", "Safety"
        CUSTOM = "custom", "Custom"

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField(blank=True)
    query_config = models.JSONField(default=dict, blank=True)
    schedule = models.CharField(max_length=100, blank=True)
    recipients = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class KPI(TenantModel):
    """Key Performance Indicator tracking."""

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    target = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, null=True, blank=True, related_name="kpis")

    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"

    def __str__(self):
        return f"{self.name}: {self.value}"
