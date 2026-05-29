"""
Client Collaboration Portal serializers.

Two sets:
  Contractor-facing  — Full read/write access to all portal management models
  Client-facing      — Scoped to what the portal client should see (no internal data)
"""

from rest_framework import serializers

from apps.clients.models import (
    ClientApproval,
    ClientMessage,
    ClientPortalAccess,
    ClientSatisfactionSurvey,
    PortalBranding,
    Selection,
    SelectionOption,
)


# ---------------------------------------------------------------------------
# Shared sub-serializers
# ---------------------------------------------------------------------------

class SelectionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectionOption
        fields = [
            "id", "name", "description", "price", "price_difference",
            "lead_time_days", "supplier", "image", "spec_sheet_url",
            "is_recommended", "sort_order",
        ]
        read_only_fields = ["id"]


class SelectionOptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectionOption
        fields = [
            "selection", "name", "description", "price", "price_difference",
            "lead_time_days", "supplier", "image", "spec_sheet_url",
            "is_recommended", "sort_order",
        ]


# ---------------------------------------------------------------------------
# Contractor-facing serializers
# ---------------------------------------------------------------------------

class ClientPortalAccessListSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.__str__", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = ClientPortalAccess
        fields = [
            "id", "contact", "contact_name", "project", "project_name",
            "email", "is_active", "last_login", "created_at",
        ]
        read_only_fields = ["id", "last_login", "created_at"]


class ClientPortalAccessDetailSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.__str__", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = ClientPortalAccess
        fields = [
            "id", "contact", "contact_name", "project", "project_name",
            "email", "pin_code", "is_active", "last_login",
            "permissions", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "access_token", "last_login", "created_at", "updated_at"]
        extra_kwargs = {
            "pin_code": {"write_only": True},
        }


class ClientPortalAccessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPortalAccess
        fields = ["contact", "project", "email", "pin_code", "permissions"]

    def validate(self, data):
        contact = data.get("contact")
        if not data.get("email") and contact and contact.email:
            data["email"] = contact.email
        if not data.get("email"):
            raise serializers.ValidationError({"email": "Email is required (contact has no email)."})
        return data


class SelectionListSerializer(serializers.ModelSerializer):
    selected_option_name = serializers.CharField(
        source="selected_option.name", read_only=True, default=None
    )

    class Meta:
        model = Selection
        fields = [
            "id", "project", "category", "name", "status",
            "selected_option", "selected_option_name", "due_date",
            "assigned_to_client", "sort_order",
        ]
        read_only_fields = ["id"]


class SelectionDetailSerializer(serializers.ModelSerializer):
    options = SelectionOptionSerializer(many=True, read_only=True)
    selected_option_detail = SelectionOptionSerializer(source="selected_option", read_only=True)

    class Meta:
        model = Selection
        fields = [
            "id", "project", "category", "name", "description", "status",
            "selected_option", "selected_option_detail", "options",
            "due_date", "assigned_to_client", "sort_order",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SelectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Selection
        fields = [
            "project", "category", "name", "description",
            "due_date", "assigned_to_client", "sort_order",
        ]


class ClientApprovalListSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.__str__", read_only=True, default=None)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = ClientApproval
        fields = [
            "id", "project", "project_name", "contact", "contact_name",
            "approval_type", "title", "status",
            "requested_at", "expires_at", "responded_at",
        ]
        read_only_fields = ["id", "requested_at"]


class ClientApprovalDetailSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.__str__", read_only=True, default=None)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = ClientApproval
        fields = [
            "id", "project", "project_name", "contact", "contact_name",
            "approval_type", "title", "description",
            "source_type", "source_id",
            "status", "requested_at", "expires_at", "responded_at",
            "response_notes", "client_signature",
            "reminded_count", "last_reminded_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "requested_at", "reminded_count", "last_reminded_at", "created_at", "updated_at"]


class ClientApprovalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientApproval
        fields = [
            "project", "contact", "approval_type", "title", "description",
            "source_type", "source_id", "expires_at",
        ]


class ClientMessageListSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = ClientMessage
        fields = [
            "id", "project", "sender_type", "sender_name",
            "subject", "body", "is_read", "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_sender_name(self, obj):
        if obj.sender_type == ClientMessage.SenderType.CONTRACTOR and obj.sender_user:
            return obj.sender_user.get_full_name() or obj.sender_user.email
        elif obj.sender_type == ClientMessage.SenderType.CLIENT and obj.sender_contact:
            return str(obj.sender_contact)
        return "Unknown"


class ClientMessageDetailSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = ClientMessage
        fields = [
            "id", "project", "sender_type", "sender_name",
            "sender_user", "sender_contact",
            "subject", "body", "is_read", "read_at",
            "attachments", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_sender_name(self, obj):
        if obj.sender_type == ClientMessage.SenderType.CONTRACTOR and obj.sender_user:
            return obj.sender_user.get_full_name() or obj.sender_user.email
        elif obj.sender_type == ClientMessage.SenderType.CLIENT and obj.sender_contact:
            return str(obj.sender_contact)
        return "Unknown"


class ClientMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientMessage
        fields = ["project", "subject", "body", "attachments"]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["sender_type"] = ClientMessage.SenderType.CONTRACTOR
        validated_data["sender_user"] = request.user if request else None
        validated_data["organization"] = validated_data["project"].organization
        return super().create(validated_data)


class PortalBrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalBranding
        fields = [
            "id", "logo", "primary_color", "secondary_color",
            "company_name_override", "welcome_message", "custom_domain",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClientSatisfactionSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSatisfactionSurvey
        fields = [
            "id", "project", "contact", "milestone",
            "rating", "nps_score", "feedback", "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]


# ---------------------------------------------------------------------------
# Client-facing portal serializers
# (No internal cost data, no other contacts' info, client-friendly language)
# ---------------------------------------------------------------------------

class PortalProjectSerializer(serializers.Serializer):
    """
    Lightweight project overview for the client portal dashboard.

    Surfaces only public-facing fields — no internal notes, cost data,
    profit margins, or staff assignments.
    """
    id = serializers.UUIDField()
    name = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField(source="get_status_display")
    address = serializers.CharField(source="site_address", default="")
    estimated_start = serializers.DateField(source="start_date")
    estimated_completion = serializers.DateField(source="target_completion")
    actual_completion = serializers.DateField()
    percent_complete = serializers.IntegerField(default=0)


class PortalSelectionOptionSerializer(serializers.ModelSerializer):
    """Client-facing selection option — hides internal cost field."""

    class Meta:
        model = SelectionOption
        fields = [
            "id", "name", "description", "price",
            "price_difference", "lead_time_days", "supplier",
            "image", "spec_sheet_url", "is_recommended", "sort_order",
        ]


class PortalSelectionSerializer(serializers.ModelSerializer):
    """Client-facing selection with options list."""
    options = PortalSelectionOptionSerializer(many=True, read_only=True)
    selected_option_detail = PortalSelectionOptionSerializer(
        source="selected_option", read_only=True
    )
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Selection
        fields = [
            "id", "category", "category_display", "name", "description",
            "status", "status_display",
            "selected_option", "selected_option_detail", "options",
            "due_date",
        ]
        read_only_fields = ["id", "status"]


class PortalSelectionChoiceSerializer(serializers.Serializer):
    """Client submits their selection choice."""
    option_id = serializers.UUIDField()


class PortalApprovalSerializer(serializers.ModelSerializer):
    """Client-facing approval request — read-only status/metadata."""
    approval_type_display = serializers.CharField(source="get_approval_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ClientApproval
        fields = [
            "id", "approval_type", "approval_type_display",
            "title", "description",
            "status", "status_display",
            "requested_at", "expires_at", "responded_at", "response_notes",
        ]
        read_only_fields = ["id", "requested_at", "status"]


class PortalApprovalResponseSerializer(serializers.Serializer):
    """Client submits an approval/rejection decision."""
    approved = serializers.BooleanField()
    response_notes = serializers.CharField(required=False, allow_blank=True, default="")
    signature_data = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Base64-encoded PNG signature image",
    )


class PortalMessageSerializer(serializers.ModelSerializer):
    """Client-facing message in conversation thread."""
    sender_name = serializers.SerializerMethodField()
    is_from_contractor = serializers.SerializerMethodField()

    class Meta:
        model = ClientMessage
        fields = [
            "id", "sender_type", "sender_name", "is_from_contractor",
            "subject", "body", "is_read", "attachments", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_sender_name(self, obj):
        if obj.sender_type == ClientMessage.SenderType.CONTRACTOR:
            if obj.sender_user:
                return obj.sender_user.get_full_name() or "Project Team"
            return "Project Team"
        elif obj.sender_contact:
            return str(obj.sender_contact)
        return "You"

    def get_is_from_contractor(self, obj):
        return obj.sender_type == ClientMessage.SenderType.CONTRACTOR


class PortalMessageSendSerializer(serializers.Serializer):
    """Client sending a new message."""
    subject = serializers.CharField(max_length=300, required=False, allow_blank=True, default="")
    body = serializers.CharField()


class PortalSurveySubmitSerializer(serializers.ModelSerializer):
    """Client submitting a satisfaction survey."""

    class Meta:
        model = ClientSatisfactionSurvey
        fields = ["rating", "nps_score", "feedback", "milestone"]
        extra_kwargs = {
            "milestone": {"required": False, "allow_blank": True},
            "nps_score": {"required": False},
        }


class PortalBrandingPublicSerializer(serializers.ModelSerializer):
    """Public branding info returned to unauthenticated/portal users."""

    class Meta:
        model = PortalBranding
        fields = [
            "primary_color", "secondary_color",
            "company_name_override", "welcome_message", "logo",
        ]


class PortalDashboardSerializer(serializers.Serializer):
    """
    Top-level payload returned by ClientDashboardView.

    Aggregates project info + pending actions + recent activity.
    """
    project = PortalProjectSerializer()
    pending_selections = serializers.IntegerField()
    pending_approvals = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    branding = PortalBrandingPublicSerializer(allow_null=True)
