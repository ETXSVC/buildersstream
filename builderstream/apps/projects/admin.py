"""Project admin configuration."""
from django.contrib import admin

from .models import (
    ActionItem,
    ActivityLog,
    DashboardLayout,
    Project,
    ProjectMilestone,
    ProjectStageTransition,
    ProjectTeamMember,
)


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 0
    readonly_fields = ["added_at"]


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "project_number", "name", "organization", "status",
        "project_type", "health_status", "estimated_value",
    ]
    list_filter = ["status", "project_type", "health_status", "is_active", "is_archived"]
    search_fields = ["name", "project_number"]
    readonly_fields = ["project_number", "health_score", "health_status"]
    inlines = [ProjectTeamMemberInline, ProjectMilestoneInline]


@admin.register(ProjectStageTransition)
class ProjectStageTransitionAdmin(admin.ModelAdmin):
    list_display = ["project", "from_status", "to_status", "transitioned_by", "created_at"]
    list_filter = ["from_status", "to_status"]
    readonly_fields = [
        "project", "from_status", "to_status", "transitioned_by",
        "requirements_met", "created_at",
    ]


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = [
        "title", "organization", "project", "item_type",
        "priority", "assigned_to", "is_resolved", "due_date",
    ]
    list_filter = ["item_type", "priority", "is_resolved"]
    search_fields = ["title"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        "organization", "project", "user", "action",
        "entity_type", "created_at",
    ]
    list_filter = ["action"]
    readonly_fields = [
        "organization", "project", "user", "action",
        "entity_type", "entity_id", "metadata", "created_at",
    ]


@admin.register(DashboardLayout)
class DashboardLayoutAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "is_default"]
