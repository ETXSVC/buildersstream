"""Analytics & Reporting Engine serializers."""
from rest_framework import serializers

from .models import Dashboard, KPI, Report


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = [
            "id", "name", "description", "layout", "widget_config", "is_default",
            "organization", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class ReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id", "name", "report_type", "description", "is_active",
            "schedule", "last_run_at", "created_at",
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "id", "name", "report_type", "description", "query_config",
            "schedule", "recipients", "is_active",
            "last_run_at", "last_run_result",
            "organization", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "last_run_at", "last_run_result",
            "organization", "created_by", "created_at", "updated_at",
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "name", "report_type", "description", "query_config",
            "schedule", "recipients", "is_active",
        ]


class KPIListSerializer(serializers.ModelSerializer):
    is_on_target = serializers.BooleanField(read_only=True)

    class Meta:
        model = KPI
        fields = [
            "id", "name", "category", "value", "target", "unit",
            "trend", "variance_percent", "is_on_target",
            "period_start", "period_end", "project",
        ]


class KPIDetailSerializer(serializers.ModelSerializer):
    is_on_target = serializers.BooleanField(read_only=True)

    class Meta:
        model = KPI
        fields = [
            "id", "name", "category", "value", "target", "unit",
            "trend", "variance_percent", "is_on_target",
            "period_start", "period_end", "project",
            "organization", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "trend", "variance_percent",
            "organization", "created_by", "created_at", "updated_at",
        ]


class KPICreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = [
            "name", "category", "value", "target", "unit",
            "period_start", "period_end", "project",
        ]
