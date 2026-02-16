"""Payroll serializers."""
from rest_framework import serializers

from .models import CertifiedPayroll, PayPeriod, PayrollRecord


class PayPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayPeriod
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class PayrollRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRecord
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class CertifiedPayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertifiedPayroll
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
