"""Analytics serializers."""
from rest_framework import serializers

from .models import Dashboard, KPI, Report


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
