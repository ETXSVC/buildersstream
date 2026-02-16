"""Service serializers."""
from rest_framework import serializers

from .models import ServiceTicket, WarrantyItem


class ServiceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTicket
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class WarrantyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyItem
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]
