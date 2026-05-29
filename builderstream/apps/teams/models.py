"""Teams — reusable named groups of employees assignable to projects."""
import uuid

from django.db import models

from apps.core.models import TenantModel, TimeStampedModel


class Team(TenantModel):
    """A named group of platform users belonging to an organization."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = [["organization", "name"]]

    def __str__(self):
        return self.name


class TeamMember(TimeStampedModel):
    """Through model linking an Employee to a Team with an optional role."""

    class Role(models.TextChoices):
        LEAD = "lead", "Team Lead"
        MEMBER = "member", "Member"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    employee = models.ForeignKey(
        "payroll.Employee",
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        unique_together = [["team", "employee"]]
        ordering = ["role", "created_at"]

    def __str__(self):
        return f"{self.employee} → {self.team} ({self.role})"
