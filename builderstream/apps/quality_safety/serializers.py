"""Quality & Safety serializers."""
from rest_framework import serializers

from .models import (
    ChecklistItem,
    Deficiency,
    Inspection,
    InspectionChecklist,
    InspectionResult,
    SafetyIncident,
    ToolboxTalk,
)


# ---------------------------------------------------------------------------
# ChecklistItem
# ---------------------------------------------------------------------------

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ["id", "description", "is_required", "sort_order"]


# ---------------------------------------------------------------------------
# InspectionChecklist
# ---------------------------------------------------------------------------

class InspectionChecklistListSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = InspectionChecklist
        fields = [
            "id", "name", "checklist_type", "category", "description",
            "is_template", "is_active", "item_count", "created_at",
        ]


class InspectionChecklistDetailSerializer(serializers.ModelSerializer):
    items = ChecklistItemSerializer(many=True, read_only=True)

    class Meta:
        model = InspectionChecklist
        fields = [
            "id", "name", "checklist_type", "category", "description",
            "is_template", "is_active", "items", "created_at", "updated_at",
        ]


class InspectionChecklistCreateSerializer(serializers.ModelSerializer):
    items = ChecklistItemSerializer(many=True, required=False)

    class Meta:
        model = InspectionChecklist
        fields = [
            "name", "checklist_type", "category", "description",
            "is_template", "is_active", "items",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        checklist = InspectionChecklist.objects.create(**validated_data)
        for i, item_data in enumerate(items_data):
            item_data.setdefault("sort_order", i)
            ChecklistItem.objects.create(checklist=checklist, **item_data)
        return checklist


# ---------------------------------------------------------------------------
# InspectionResult
# ---------------------------------------------------------------------------

class InspectionResultSerializer(serializers.ModelSerializer):
    item_description = serializers.CharField(
        source="checklist_item.description", read_only=True
    )
    item_required = serializers.BooleanField(
        source="checklist_item.is_required", read_only=True
    )

    class Meta:
        model = InspectionResult
        fields = [
            "id", "checklist_item", "item_description", "item_required",
            "status", "notes", "photo",
        ]


class RecordResultsSerializer(serializers.Serializer):
    results = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of {checklist_item_id, status, notes, photo_id}",
    )
    final_status = serializers.ChoiceField(
        choices=Inspection.Status.choices,
        required=False,
        allow_null=True,
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------

class InspectionListSerializer(serializers.ModelSerializer):
    checklist_name = serializers.CharField(source="checklist.name", read_only=True)
    checklist_category = serializers.CharField(source="checklist.category", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    inspector_name = serializers.SerializerMethodField()

    class Meta:
        model = Inspection
        fields = [
            "id", "project", "project_name", "checklist", "checklist_name",
            "checklist_category", "inspector", "inspector_name",
            "inspection_date", "status", "overall_score", "created_at",
        ]

    def get_inspector_name(self, obj):
        if obj.inspector_id:
            return f"{obj.inspector.first_name} {obj.inspector.last_name}".strip()
        return None


class InspectionDetailSerializer(serializers.ModelSerializer):
    checklist_name = serializers.CharField(source="checklist.name", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    results = InspectionResultSerializer(many=True, read_only=True)
    deficiency_count = serializers.IntegerField(
        source="deficiencies.count", read_only=True
    )

    class Meta:
        model = Inspection
        fields = [
            "id", "project", "project_name", "checklist", "checklist_name",
            "inspector", "inspection_date", "status", "overall_score", "notes",
            "photos", "results", "deficiency_count", "created_at", "updated_at",
        ]


class InspectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = ["project", "checklist", "inspector", "inspection_date", "notes"]


# ---------------------------------------------------------------------------
# Deficiency
# ---------------------------------------------------------------------------

class DeficiencyListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Deficiency
        fields = [
            "id", "project", "project_name", "title", "severity", "status",
            "assigned_to", "assigned_to_name", "due_date", "resolved_date", "created_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to_id:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip()
        return None


class DeficiencyDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Deficiency
        fields = [
            "id", "project", "project_name", "inspection", "title", "description",
            "severity", "status", "assigned_to", "due_date", "resolved_date",
            "resolved_by", "verified_by", "resolution_notes", "photos",
            "created_at", "updated_at",
        ]


class DeficiencyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deficiency
        fields = [
            "project", "inspection", "title", "description",
            "severity", "assigned_to", "due_date",
        ]


class ResolveDeficiencySerializer(serializers.Serializer):
    notes = serializers.CharField(required=True, min_length=1)


# ---------------------------------------------------------------------------
# SafetyIncident
# ---------------------------------------------------------------------------

class SafetyIncidentListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    reported_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SafetyIncident
        fields = [
            "id", "project", "project_name", "incident_date", "incident_type",
            "severity", "status", "osha_reportable", "reported_by",
            "reported_by_name", "created_at",
        ]

    def get_reported_by_name(self, obj):
        if obj.reported_by_id:
            return f"{obj.reported_by.first_name} {obj.reported_by.last_name}".strip()
        return None


class SafetyIncidentDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = SafetyIncident
        fields = [
            "id", "project", "project_name", "incident_date", "incident_type",
            "severity", "description", "reported_by", "witnesses",
            "injured_person_name", "root_cause", "corrective_actions",
            "osha_reportable", "photos", "status", "created_at", "updated_at",
        ]


class SafetyIncidentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyIncident
        fields = [
            "project", "incident_date", "incident_type", "severity",
            "description", "witnesses", "injured_person_name", "osha_reportable",
        ]


class CloseIncidentSerializer(serializers.Serializer):
    corrective_notes = serializers.CharField(required=False, allow_blank=True, default="")


# ---------------------------------------------------------------------------
# ToolboxTalk
# ---------------------------------------------------------------------------

class ToolboxTalkListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    attendee_count = serializers.IntegerField(source="attendees.count", read_only=True)

    class Meta:
        model = ToolboxTalk
        fields = [
            "id", "project", "project_name", "topic", "presented_by",
            "presented_date", "attendee_count", "created_at",
        ]


class ToolboxTalkDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    attendee_count = serializers.IntegerField(source="attendees.count", read_only=True)

    class Meta:
        model = ToolboxTalk
        fields = [
            "id", "project", "project_name", "topic", "content",
            "presented_by", "presented_date", "attendees", "attendee_count",
            "sign_in_sheet", "created_at", "updated_at",
        ]


class ToolboxTalkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolboxTalk
        fields = ["project", "topic", "content", "presented_by", "presented_date", "attendees"]
