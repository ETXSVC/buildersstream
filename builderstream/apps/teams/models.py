"""Teams — reusable named groups of users assignable to projects."""
import uuid

from django.conf import settings
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
    """Through model linking a User to a Team with an optional role."""

    class Role(models.TextChoices):
        LEAD = "lead", "Team Lead"
        MEMBER = "member", "Member"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        unique_together = [["team", "user"]]
        ordering = ["role", "created_at"]

    def __str__(self):
        return f"{self.user} → {self.team} ({self.role})"
