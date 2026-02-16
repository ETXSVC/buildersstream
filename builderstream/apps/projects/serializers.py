"""Project serializers."""
from rest_framework import serializers

from .models import (
    ActionItem,
    ActivityLog,
    DashboardLayout,
    Project,
    ProjectMilestone,
    ProjectStageTransition,
    ProjectTeamMember,
)


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTeamMember
        fields = ["id", "user", "user_name", "role", "added_at"]
        read_only_fields = ["id", "added_at"]

    def get_user_name(self, obj):
        return obj.user.get_full_name()


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = [
            "id", "project", "name", "description", "due_date",
            "completed_date", "is_completed", "sort_order",
            "notify_client", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProjectListSerializer(serializers.ModelSerializer):
    """Compact serializer for project list views."""

    client_name = serializers.SerializerMethodField()
    project_manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name", "project_number", "status", "project_type",
            "client", "client_name", "city", "state",
            "estimated_value", "start_date", "estimated_completion",
            "health_score", "health_status", "completion_percentage",
            "project_manager", "project_manager_name",
            "is_active", "is_archived", "created_at",
        ]
        read_only_fields = fields

    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None

    def get_project_manager_name(self, obj):
        return obj.project_manager.get_full_name() if obj.project_manager else None


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full serializer for project detail views."""

    client_name = serializers.SerializerMethodField()
    project_manager_name = serializers.SerializerMethodField()
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "name", "project_number", "description",
            "status", "project_type",
            "client", "client_name",
            "address", "city", "state", "zip_code",
            "latitude", "longitude",
            "estimated_value", "actual_revenue",
            "estimated_cost", "actual_cost",
            "start_date", "estimated_completion", "actual_completion",
            "project_manager", "project_manager_name",
            "team_members", "milestones",
            "health_score", "health_status", "completion_percentage",
            "tags", "custom_fields",
            "is_active", "is_archived",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "project_number", "organization",
            "health_score", "health_status",
            "created_by", "created_at", "updated_at",
        ]

    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None

    def get_project_manager_name(self, obj):
        return obj.project_manager.get_full_name() if obj.project_manager else None


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating projects (project_number auto-generated)."""

    class Meta:
        model = Project
        fields = [
            "name", "description", "project_type",
            "client", "address", "city", "state", "zip_code",
            "latitude", "longitude",
            "estimated_value", "estimated_cost",
            "start_date", "estimated_completion",
            "project_manager", "tags", "custom_fields",
        ]

    def create(self, validated_data):
        from .services import ProjectNumberService

        org = self.context.get("organization")
        if org:
            validated_data["project_number"] = (
                ProjectNumberService.generate_project_number(org)
            )
        else:
            # Fallback — should not normally happen with TenantViewSetMixin
            import uuid
            validated_data["project_number"] = f"BSP-TMP-{str(uuid.uuid4())[:8]}"

        return super().create(validated_data)


class ProjectStatusTransitionSerializer(serializers.Serializer):
    """Serializer for status transition requests."""

    new_status = serializers.ChoiceField(choices=Project.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class StageTransitionLogSerializer(serializers.ModelSerializer):
    """Read-only serializer for transition audit log."""

    transitioned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectStageTransition
        fields = [
            "id", "from_status", "to_status",
            "transitioned_by", "transitioned_by_name",
            "notes", "requirements_met", "created_at",
        ]
        read_only_fields = fields

    def get_transitioned_by_name(self, obj):
        return obj.transitioned_by.get_full_name() if obj.transitioned_by else None


class ActionItemSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = ActionItem
        fields = [
            "id", "organization", "project", "project_name",
            "title", "description", "item_type", "priority",
            "assigned_to", "assigned_to_name", "due_date",
            "is_resolved", "resolved_at",
            "source_type", "source_id", "created_at",
        ]
        read_only_fields = ["id", "organization", "created_at", "resolved_at"]

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else None

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = [
            "id", "project", "project_name",
            "user", "user_name", "action",
            "entity_type", "entity_id",
            "description", "metadata", "created_at",
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else None

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None


class DashboardSerializer(serializers.Serializer):
    """Read-only serializer for dashboard aggregate data."""

    active_projects = serializers.DictField()
    financial_snapshot = serializers.DictField()
    schedule_overview = serializers.DictField()
    action_items = serializers.ListField()
    activity_stream = serializers.ListField()
    weather = serializers.DictField()


class DashboardLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardLayout
        fields = ["id", "layout", "is_default", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
