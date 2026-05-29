"""Analytics & Reporting Engine models."""
from django.db import models

from apps.core.models import TenantModel


class Dashboard(TenantModel):
    """Custom dashboard configuration for an organization user."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    layout = models.JSONField(default=dict, blank=True)
    widget_config = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "name"]
        indexes = [
            models.Index(fields=["organization", "is_default"], name="analytics_dash_org_default_idx"),
        ]

    def __str__(self):
        return self.name


class Report(TenantModel):
    """Saved report definition --- stores config and last execution result."""

    class ReportType(models.TextChoices):
        FINANCIAL = "financial", "Financial"
        PROJECT = "project", "Project"
        LABOR = "labor", "Labor"
        SAFETY = "safety", "Safety"
        SERVICE = "service", "Service"
        CUSTOM = "custom", "Custom"

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    description = models.TextField(blank=True)
    query_config = models.JSONField(default=dict, blank=True)
    schedule = models.CharField(max_length=100, blank=True)
    recipients = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_run_result = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["organization", "report_type"], name="analytics_rpt_org_type_idx"),
            models.Index(fields=["organization", "is_active"], name="analytics_rpt_org_active_idx"),
        ]

    def __str__(self):
        return self.name


class KPI(TenantModel):
    """Key Performance Indicator --- a single metric for a given period."""

    class Category(models.TextChoices):
        FINANCIAL = "financial", "Financial"
        PROJECT = "project", "Project"
        LABOR = "labor", "Labor"
        SAFETY = "safety", "Safety"
        SERVICE = "service", "Service"

    class Trend(models.TextChoices):
        UP = "up", "Up"
        DOWN = "down", "Down"
        STABLE = "stable", "Stable"

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=Category.choices)
    value = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    target = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    period_start = models.DateField()
    period_end = models.DateField()
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="kpis",
    )
    trend = models.CharField(
        max_length=10, choices=Trend.choices, default=Trend.STABLE
    )
    variance_percent = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"
        ordering = ["-period_end", "category", "name"]
        indexes = [
            models.Index(fields=["organization", "category"], name="analytics_kpi_org_cat_idx"),
            models.Index(fields=["organization", "-period_end"], name="analytics_kpi_org_period_idx"),
            models.Index(fields=["organization", "project"], name="analytics_kpi_org_proj_idx"),
        ]

    def __str__(self):
        return f"{self.name}: {self.value} ({self.unit})"

    @property
    def is_on_target(self):
        if self.value is None or self.target is None:
            return None
        return self.value >= self.target
