"""Scheduling serializers."""
from rest_framework import serializers

from .models import Crew, ScheduleTask


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class ScheduleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleTask
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
