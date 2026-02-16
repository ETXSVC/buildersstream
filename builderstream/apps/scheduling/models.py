"""Scheduling models: Gantt, resource allocation, crews."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Crew(TenantModel):
    """Work crew for resource allocation."""

    name = models.CharField(max_length=100)
    foreman = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="crews_led",
    )
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="crews")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ScheduleTask(TenantModel):
    """Individual task in the project schedule (Gantt)."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        DELAYED = "delayed", "Delayed"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="schedule_tasks")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.PositiveIntegerField(default=1)
    progress = models.PositiveIntegerField(default=0)
    parent_task = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks")
    predecessor = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="successors")
    crew = models.ForeignKey(Crew, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "start_date"]

    def __str__(self):
        return self.name
