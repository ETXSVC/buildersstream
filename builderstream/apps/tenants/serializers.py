"""Tenant serializers."""
from rest_framework import serializers

from .models import ActiveModule, Organization, OrganizationMembership


class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id", "name", "slug", "owner", "logo",
            "phone", "email", "website",
            "address_line1", "address_line2", "city", "state", "zip_code", "country",
            "industry_type",
            "subscription_plan", "subscription_status", "trial_ends_at", "max_users",
            "is_active", "settings", "member_count",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "owner", "stripe_customer_id", "stripe_subscription_id",
            "subscription_status", "member_count", "created_at", "updated_at",
        ]


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationMembership
        fields = [
            "id", "user", "user_email", "user_full_name",
            "organization", "role", "is_active",
            "invited_by", "invited_at", "accepted_at",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "user", "organization", "invited_by",
            "invited_at", "accepted_at", "created_at", "updated_at",
        ]

    def get_user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=OrganizationMembership.Role.choices,
        default=OrganizationMembership.Role.READ_ONLY,
    )


class ModuleActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveModule
        fields = [
            "id", "organization", "module_key", "is_active", "activated_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "activated_at", "created_at", "updated_at"]
