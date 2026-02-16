"""Estimating serializers."""
from rest_framework import serializers

from .models import CostCode, Estimate, EstimateLineItem


class CostCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCode
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class EstimateLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimateLineItem
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at", "total"]


class EstimateSerializer(serializers.ModelSerializer):
    line_items = EstimateLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Estimate
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
