"""Tenant serializers."""
from rest_framework import serializers

from .models import Membership, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id", "name", "slug", "logo", "website", "phone",
            "address_line1", "address_line2", "city", "state",
            "zip_code", "country", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = [
            "id", "user", "organization", "role", "is_active",
            "invited_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "invited_by", "created_at", "updated_at"]
