"""CRM serializers."""
from rest_framework import serializers

from apps.accounts.serializers import UserProfileSerializer

from .models import (
    AutomationRule,
    Company,
    Contact,
    EmailTemplate,
    Interaction,
    Lead,
    PipelineStage,
)


# ===== Contact Serializers =====

class ContactListSerializer(serializers.ModelSerializer):
    """Compact contact list view."""

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "mobile_phone",
            "company_name",
            "contact_type",
            "source",
            "lead_score",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "lead_score"]


class ContactDetailSerializer(serializers.ModelSerializer):
    """Full contact details with nested data."""

    company_detail = serializers.SerializerMethodField()
    referred_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "mobile_phone",
            "company",
            "company_detail",
            "company_name",
            "job_title",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "zip_code",
            "contact_type",
            "source",
            "referred_by",
            "referred_by_name",
            "lead_score",
            "tags",
            "custom_fields",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "lead_score"]

    def get_company_detail(self, obj):
        if obj.company:
            return {
                "id": obj.company.id,
                "name": obj.company.name,
                "company_type": obj.company.company_type,
            }
        return None

    def get_referred_by_name(self, obj):
        if obj.referred_by:
            return f"{obj.referred_by.first_name} {obj.referred_by.last_name}"
        return None


class ContactCreateSerializer(serializers.ModelSerializer):
    """Create/update contact."""

    class Meta:
        model = Contact
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "mobile_phone",
            "company",
            "company_name",
            "job_title",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "zip_code",
            "contact_type",
            "source",
            "referred_by",
            "tags",
            "custom_fields",
            "notes",
            "is_active",
        ]


# ===== Company Serializers =====

class CompanyListSerializer(serializers.ModelSerializer):
    """Compact company list view."""

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "company_type",
            "performance_rating",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CompanyDetailSerializer(serializers.ModelSerializer):
    """Full company details with contacts."""

    contact_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "website",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "zip_code",
            "company_type",
            "insurance_expiry",
            "license_number",
            "license_expiry",
            "performance_rating",
            "notes",
            "contact_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_contact_count(self, obj):
        return obj.contacts.count()


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Create/update company."""

    class Meta:
        model = Company
        fields = [
            "name",
            "phone",
            "email",
            "website",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "zip_code",
            "company_type",
            "insurance_expiry",
            "license_number",
            "license_expiry",
            "performance_rating",
            "notes",
        ]


# ===== PipelineStage Serializers =====

class PipelineStageSerializer(serializers.ModelSerializer):
    """Pipeline stage serializer."""

    lead_count = serializers.SerializerMethodField()

    class Meta:
        model = PipelineStage
        fields = [
            "id",
            "name",
            "sort_order",
            "color",
            "is_won_stage",
            "is_lost_stage",
            "auto_actions",
            "lead_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_lead_count(self, obj):
        return obj.leads.count()


# ===== Lead Serializers =====

class LeadListSerializer(serializers.ModelSerializer):
    """Compact lead list view."""

    contact_name = serializers.SerializerMethodField()
    stage_name = serializers.CharField(source="pipeline_stage.name", read_only=True)
    stage_color = serializers.CharField(source="pipeline_stage.color", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "contact",
            "contact_name",
            "pipeline_stage",
            "stage_name",
            "stage_color",
            "project_type",
            "estimated_value",
            "urgency",
            "assigned_to",
            "assigned_to_name",
            "last_contacted_at",
            "next_follow_up",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_contact_name(self, obj):
        return f"{obj.contact.first_name} {obj.contact.last_name}"


class LeadDetailSerializer(serializers.ModelSerializer):
    """Full lead details."""

    contact_detail = ContactDetailSerializer(source="contact", read_only=True)
    stage_detail = PipelineStageSerializer(source="pipeline_stage", read_only=True)
    assigned_to_detail = UserProfileSerializer(source="assigned_to", read_only=True)
    interaction_count = serializers.SerializerMethodField()
    converted_project_number = serializers.CharField(
        source="converted_project.project_number",
        read_only=True,
    )

    class Meta:
        model = Lead
        fields = [
            "id",
            "contact",
            "contact_detail",
            "pipeline_stage",
            "stage_detail",
            "assigned_to",
            "assigned_to_detail",
            "project_type",
            "estimated_value",
            "estimated_start",
            "urgency",
            "description",
            "lost_reason",
            "lost_to_competitor",
            "converted_project",
            "converted_project_number",
            "last_contacted_at",
            "next_follow_up",
            "interaction_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_interaction_count(self, obj):
        return obj.interactions.count()


class LeadCreateSerializer(serializers.ModelSerializer):
    """Create/update lead."""

    class Meta:
        model = Lead
        fields = [
            "contact",
            "pipeline_stage",
            "assigned_to",
            "project_type",
            "estimated_value",
            "estimated_start",
            "urgency",
            "description",
            "lost_reason",
            "lost_to_competitor",
            "last_contacted_at",
            "next_follow_up",
        ]


# ===== Interaction Serializers =====

class InteractionListSerializer(serializers.ModelSerializer):
    """Compact interaction list view."""

    contact_name = serializers.SerializerMethodField()
    logged_by_name = serializers.CharField(
        source="logged_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Interaction
        fields = [
            "id",
            "contact",
            "contact_name",
            "lead",
            "interaction_type",
            "direction",
            "subject",
            "occurred_at",
            "logged_by",
            "logged_by_name",
        ]
        read_only_fields = ["id"]

    def get_contact_name(self, obj):
        return f"{obj.contact.first_name} {obj.contact.last_name}"


class InteractionDetailSerializer(serializers.ModelSerializer):
    """Full interaction details."""

    contact_detail = ContactListSerializer(source="contact", read_only=True)
    logged_by_detail = UserProfileSerializer(source="logged_by", read_only=True)

    class Meta:
        model = Interaction
        fields = [
            "id",
            "contact",
            "contact_detail",
            "lead",
            "interaction_type",
            "direction",
            "subject",
            "body",
            "occurred_at",
            "logged_by",
            "logged_by_detail",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InteractionCreateSerializer(serializers.ModelSerializer):
    """Create/update interaction."""

    class Meta:
        model = Interaction
        fields = [
            "contact",
            "lead",
            "interaction_type",
            "direction",
            "subject",
            "body",
            "occurred_at",
            "logged_by",
        ]


# ===== AutomationRule Serializers =====

class AutomationRuleSerializer(serializers.ModelSerializer):
    """Automation rule serializer."""

    class Meta:
        model = AutomationRule
        fields = [
            "id",
            "name",
            "is_active",
            "trigger_type",
            "trigger_config",
            "action_type",
            "action_config",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ===== EmailTemplate Serializers =====

class EmailTemplateSerializer(serializers.ModelSerializer):
    """Email template serializer."""

    class Meta:
        model = EmailTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "subject",
            "body",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ===== Special Serializers =====

class PipelineBoardSerializer(serializers.Serializer):
    """Kanban-style pipeline board data."""

    stages = PipelineStageSerializer(many=True)
    leads_by_stage = serializers.DictField(child=LeadListSerializer(many=True))


class LeadAnalyticsSerializer(serializers.Serializer):
    """Lead analytics data."""

    conversion_by_source = serializers.DictField()
    conversion_by_assigned_to = serializers.DictField()
    conversion_by_project_type = serializers.DictField()
    win_loss_reasons = serializers.DictField()
    avg_time_in_stage = serializers.DictField()
    lead_velocity = serializers.DictField()
