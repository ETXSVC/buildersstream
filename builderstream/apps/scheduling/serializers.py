"""Scheduling serializers."""
from rest_framework import serializers

from .models import Crew, Equipment, Task, TaskDependency


class CrewSerializer(serializers.ModelSerializer):
    foreman_name = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = [
            "id", "organization", "name", "trade", "foreman", "foreman_name",
            "members", "member_count", "hourly_rate", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_at", "updated_at"]

    def get_foreman_name(self, obj):
        if obj.foreman:
            return obj.foreman.get_full_name() or obj.foreman.email
        return None

    def get_member_count(self, obj):
        return obj.members.count()


class TaskDependencySerializer(serializers.ModelSerializer):
    predecessor_name = serializers.CharField(source="predecessor.name", read_only=True)
    successor_name = serializers.CharField(source="successor.name", read_only=True)

    class Meta:
        model = TaskDependency
        fields = [
            "id", "predecessor", "predecessor_name",
            "successor", "successor_name",
            "dependency_type", "lag_days",
        ]


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists."""
    assigned_crew_name = serializers.CharField(source="assigned_crew.name", read_only=True)
    subtask_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "name", "wbs_code", "task_type", "status",
            "parent_task", "start_date", "end_date", "duration_days",
            "completion_percentage", "is_critical_path", "float_days",
            "assigned_crew", "assigned_crew_name", "sort_order",
            "subtask_count", "color",
        ]
        read_only_fields = ["id", "is_critical_path", "float_days"]

    def get_subtask_count(self, obj):
        return obj.subtasks.count()


class TaskSerializer(serializers.ModelSerializer):
    """Full task serializer with nested data."""
    assigned_crew_name = serializers.CharField(source="assigned_crew.name", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    dependencies = TaskDependencySerializer(source="predecessor_deps", many=True, read_only=True)
    successors_list = TaskDependencySerializer(source="successor_deps", many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "organization", "project", "project_name",
            "name", "description", "parent_task", "task_type", "status",
            "start_date", "end_date", "actual_start", "actual_end",
            "duration_days", "completion_percentage",
            "assigned_crew", "assigned_crew_name", "assigned_users",
            "cost_code", "estimated_hours", "actual_hours",
            "is_critical_path", "float_days",
            "early_start", "early_finish", "late_start", "late_finish",
            "sort_order", "wbs_code", "color",
            "dependencies", "successors_list",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "organization",
            "is_critical_path", "float_days",
            "early_start", "early_finish", "late_start", "late_finish",
            "created_at", "updated_at",
        ]


class EquipmentSerializer(serializers.ModelSerializer):
    current_project_name = serializers.CharField(source="current_project.name", read_only=True)
    calculated_book_value = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = [
            "id", "organization", "name", "description", "equipment_type",
            "serial_number", "status", "current_project", "current_project_name",
            "purchase_date", "purchase_cost", "depreciation_method",
            "useful_life_years", "salvage_value", "current_book_value",
            "calculated_book_value", "daily_rental_rate", "next_maintenance",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "current_book_value", "created_at", "updated_at"]

    def get_calculated_book_value(self, obj):
        return obj.calculate_book_value()


class EquipmentDepreciationSerializer(serializers.Serializer):
    """Output for depreciation calculation endpoint."""
    equipment_id = serializers.UUIDField()
    name = serializers.CharField()
    purchase_cost = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    purchase_date = serializers.DateField(allow_null=True)
    depreciation_method = serializers.CharField()
    useful_life_years = serializers.IntegerField()
    salvage_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    current_book_value = serializers.FloatField()
    accumulated_depreciation = serializers.FloatField()
    net_book_value = serializers.FloatField()


class GanttDataSerializer(serializers.Serializer):
    """Gantt chart data output."""
    project_id = serializers.UUIDField()
    project_name = serializers.CharField()
    tasks = serializers.ListField()
    milestones = serializers.ListField()
    dependencies = serializers.ListField()
    crew_allocation = serializers.DictField()
    critical_path_task_ids = serializers.ListField()
    stats = serializers.DictField()


class CrewAvailabilitySerializer(serializers.Serializer):
    """Crew availability output."""
    crew_id = serializers.UUIDField()
    crew_name = serializers.CharField()
    trade = serializers.CharField()
    allocation_by_date = serializers.DictField()
    allocated_tasks = serializers.ListField()
    is_overallocated = serializers.BooleanField()
