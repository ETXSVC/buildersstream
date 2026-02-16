"""Quality and safety serializers."""
from rest_framework import serializers

from .models import Inspection, SafetyChecklist, SafetyIncident


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class SafetyIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyIncident
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class SafetyChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyChecklist
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
