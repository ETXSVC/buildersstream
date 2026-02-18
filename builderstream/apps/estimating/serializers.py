"""Estimating serializers."""
from rest_framework import serializers

from .models import (
    Assembly,
    AssemblyItem,
    CostCode,
    CostItem,
    Estimate,
    EstimateLineItem,
    EstimateSection,
    Proposal,
    ProposalTemplate,
)


# ============================================================================
# CostCode Serializers
# ============================================================================

class CostCodeListSerializer(serializers.ModelSerializer):
    """Compact serializer for cost code list views."""

    class Meta:
        model = CostCode
        fields = [
            "id", "code", "name", "division", "category",
            "is_labor", "is_active", "created_at",
        ]
        read_only_fields = fields


class CostCodeDetailSerializer(serializers.ModelSerializer):
    """Full serializer for cost code detail views."""

    cost_items_count = serializers.SerializerMethodField()

    class Meta:
        model = CostCode
        fields = [
            "id", "code", "name", "division", "category",
            "is_labor", "is_active", "cost_items_count",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_cost_items_count(self, obj):
        return obj.cost_items.count()


class CostCodeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cost codes."""

    class Meta:
        model = CostCode
        fields = ["code", "name", "division", "category", "is_labor", "is_active"]


# ============================================================================
# CostItem Serializers
# ============================================================================

class CostItemListSerializer(serializers.ModelSerializer):
    """Compact serializer for cost item list views."""

    cost_code_name = serializers.SerializerMethodField()

    class Meta:
        model = CostItem
        fields = [
            "id", "name", "cost_code", "cost_code_name", "unit",
            "cost", "base_price", "client_price", "markup_percent",
            "is_taxable", "is_active", "created_at",
        ]
        read_only_fields = [
            "id", "cost_code_name", "markup_percent", "created_at"
        ]

    def get_cost_code_name(self, obj):
        return str(obj.cost_code) if obj.cost_code else None


class CostItemDetailSerializer(serializers.ModelSerializer):
    """Full serializer for cost item detail views."""

    cost_code_name = serializers.SerializerMethodField()

    class Meta:
        model = CostItem
        fields = [
            "id", "cost_code", "cost_code_name", "name", "description",
            "unit", "cost", "base_price", "client_price", "markup_percent",
            "labor_hours", "is_taxable", "is_active", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "markup_percent", "created_at", "updated_at"]

    def get_cost_code_name(self, obj):
        return str(obj.cost_code) if obj.cost_code else None


class CostItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cost items."""

    class Meta:
        model = CostItem
        fields = [
            "cost_code", "name", "description", "unit",
            "cost", "base_price", "client_price",
            "labor_hours", "is_taxable", "notes",
        ]


# ============================================================================
# Assembly Serializers
# ============================================================================

class AssemblyItemSerializer(serializers.ModelSerializer):
    """Serializer for assembly items (nested in assembly)."""

    cost_item_name = serializers.SerializerMethodField()
    line_cost = serializers.SerializerMethodField()
    line_price = serializers.SerializerMethodField()

    class Meta:
        model = AssemblyItem
        fields = [
            "id", "cost_item", "cost_item_name", "quantity",
            "line_cost", "line_price", "sort_order", "notes",
        ]
        read_only_fields = ["id", "line_cost", "line_price"]

    def get_cost_item_name(self, obj):
        return obj.cost_item.name if obj.cost_item else None

    def get_line_cost(self, obj):
        return float(obj.line_cost)

    def get_line_price(self, obj):
        return float(obj.line_price)


class AssemblyListSerializer(serializers.ModelSerializer):
    """Compact serializer for assembly list views."""

    class Meta:
        model = Assembly
        fields = [
            "id", "name", "description", "total_cost", "total_price",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "total_cost", "total_price", "created_at"]


class AssemblyDetailSerializer(serializers.ModelSerializer):
    """Full serializer for assembly detail views."""

    assembly_items = AssemblyItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Assembly
        fields = [
            "id", "name", "description", "total_cost", "total_price",
            "assembly_items", "items_count", "is_active", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "total_cost", "total_price", "assembly_items",
            "items_count", "created_at", "updated_at",
        ]

    def get_items_count(self, obj):
        return obj.assembly_items.count()


class AssemblyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assemblies."""

    class Meta:
        model = Assembly
        fields = ["name", "description", "notes"]


class AssemblyItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating assembly items."""

    class Meta:
        model = AssemblyItem
        fields = ["assembly", "cost_item", "quantity", "sort_order", "notes"]


# ============================================================================
# Estimate Serializers
# ============================================================================

class EstimateLineItemSerializer(serializers.ModelSerializer):
    """Serializer for estimate line items (nested in section)."""

    item_name = serializers.SerializerMethodField()

    class Meta:
        model = EstimateLineItem
        fields = [
            "id", "cost_item", "assembly", "item_name", "description",
            "quantity", "unit", "unit_cost", "unit_price", "line_total",
            "is_taxable", "sort_order", "notes",
        ]
        read_only_fields = ["id", "line_total"]

    def get_item_name(self, obj):
        return (
            obj.description
            or (obj.cost_item.name if obj.cost_item else None)
            or (obj.assembly.name if obj.assembly else None)
        )


class EstimateSectionSerializer(serializers.ModelSerializer):
    """Serializer for estimate sections (nested in estimate)."""

    line_items = EstimateLineItemSerializer(many=True, read_only=True)
    line_items_count = serializers.SerializerMethodField()

    class Meta:
        model = EstimateSection
        fields = [
            "id", "name", "description", "sort_order", "subtotal",
            "line_items", "line_items_count",
        ]
        read_only_fields = ["id", "subtotal", "line_items", "line_items_count"]

    def get_line_items_count(self, obj):
        return obj.line_items.count()


class EstimateListSerializer(serializers.ModelSerializer):
    """Compact serializer for estimate list views."""

    project_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Estimate
        fields = [
            "id", "estimate_number", "name", "status",
            "project", "project_name", "lead", "lead_name",
            "subtotal", "tax_rate", "total",
            "created_by", "created_by_name",
            "valid_until", "created_at",
        ]
        read_only_fields = fields

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_lead_name(self, obj):
        return str(obj.lead.contact) if obj.lead else None

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class EstimateDetailSerializer(serializers.ModelSerializer):
    """Full serializer for estimate detail views."""

    project_name = serializers.SerializerMethodField()
    lead_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    sections = EstimateSectionSerializer(many=True, read_only=True)
    sections_count = serializers.SerializerMethodField()

    class Meta:
        model = Estimate
        fields = [
            "id", "estimate_number", "name", "status",
            "project", "project_name", "lead", "lead_name",
            "subtotal", "tax_rate", "tax_amount", "total",
            "sections", "sections_count",
            "notes", "valid_until",
            "created_by", "created_by_name",
            "approved_by", "approved_by_name", "approved_at",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "estimate_number", "subtotal", "tax_amount", "total",
            "sections", "sections_count",
            "created_by_name", "approved_by_name",
            "created_at", "updated_at",
        ]

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_lead_name(self, obj):
        return str(obj.lead.contact) if obj.lead else None

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None

    def get_sections_count(self, obj):
        return obj.sections.count()


class EstimateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating estimates."""

    class Meta:
        model = Estimate
        fields = [
            "project", "lead", "name", "tax_rate",
            "notes", "valid_until",
        ]


class EstimateSectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating estimate sections."""

    class Meta:
        model = EstimateSection
        fields = ["estimate", "name", "description", "sort_order"]


class EstimateLineItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating estimate line items."""

    class Meta:
        model = EstimateLineItem
        fields = [
            "section", "cost_item", "assembly", "description",
            "quantity", "unit", "unit_cost", "unit_price",
            "is_taxable", "sort_order", "notes",
        ]

    def validate(self, attrs):
        """Ensure either cost_item or assembly is provided, but not both."""
        cost_item = attrs.get("cost_item")
        assembly = attrs.get("assembly")

        if not cost_item and not assembly:
            raise serializers.ValidationError(
                "Either cost_item or assembly must be provided."
            )

        if cost_item and assembly:
            raise serializers.ValidationError(
                "Cannot specify both cost_item and assembly."
            )

        return attrs


# ============================================================================
# Proposal Serializers
# ============================================================================

class ProposalTemplateSerializer(serializers.ModelSerializer):
    """Serializer for proposal templates."""

    class Meta:
        model = ProposalTemplate
        fields = [
            "id", "name", "header_text", "footer_text",
            "terms_and_conditions", "signature_instructions",
            "is_default", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProposalListSerializer(serializers.ModelSerializer):
    """Compact serializer for proposal list views."""

    client_name = serializers.SerializerMethodField()
    estimate_name = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "id", "proposal_number", "status", "is_signed",
            "estimate", "estimate_name",
            "client", "client_name",
            "sent_at", "viewed_at", "signed_at",
            "view_count", "created_at",
        ]
        read_only_fields = fields

    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

    def get_estimate_name(self, obj):
        return f"{obj.estimate.estimate_number} - {obj.estimate.name}"


class ProposalDetailSerializer(serializers.ModelSerializer):
    """Full serializer for proposal detail views."""

    client_name = serializers.SerializerMethodField()
    estimate_name = serializers.SerializerMethodField()
    template_name = serializers.SerializerMethodField()
    estimate_details = EstimateDetailSerializer(source="estimate", read_only=True)

    class Meta:
        model = Proposal
        fields = [
            "id", "proposal_number", "public_token", "status", "is_signed",
            "estimate", "estimate_name", "estimate_details",
            "project", "lead", "client", "client_name",
            "template", "template_name",
            "pdf_file", "sent_at", "sent_to_email",
            "viewed_at", "view_count",
            "signed_at", "signed_by_name", "signature_image",
            "valid_until", "terms_and_conditions", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "proposal_number", "public_token",
            "client_name", "estimate_name", "template_name",
            "estimate_details", "pdf_file", "sent_at",
            "viewed_at", "view_count", "signed_at",
            "signed_by_name", "signature_image",
            "created_at", "updated_at",
        ]

    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

    def get_estimate_name(self, obj):
        return f"{obj.estimate.estimate_number} - {obj.estimate.name}"

    def get_template_name(self, obj):
        return obj.template.name if obj.template else None


class ProposalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating proposals."""

    class Meta:
        model = Proposal
        fields = [
            "estimate", "project", "lead", "client",
            "template", "valid_until", "notes",
        ]


class PublicProposalSerializer(serializers.ModelSerializer):
    """Public serializer for unauthenticated proposal viewing."""

    client_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    estimate_details = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            "proposal_number", "status", "is_signed",
            "organization_name", "client_name",
            "estimate_details",
            "pdf_file", "sent_at", "viewed_at", "view_count",
            "signed_at", "signed_by_name", "signature_image",
            "valid_until", "terms_and_conditions",
        ]
        read_only_fields = fields

    def get_client_name(self, obj):
        return f"{obj.client.first_name} {obj.client.last_name}"

    def get_organization_name(self, obj):
        return obj.organization.name

    def get_estimate_details(self, obj):
        """Return simplified estimate data (no internal costs)."""
        estimate = obj.estimate
        sections_data = []

        for section in estimate.sections.all():
            line_items_data = []
            for item in section.line_items.all():
                line_items_data.append({
                    "description": (
                        item.description
                        or (item.cost_item.name if item.cost_item else None)
                        or (item.assembly.name if item.assembly else None)
                    ),
                    "quantity": float(item.quantity),
                    "unit": item.unit,
                    "unit_price": float(item.unit_price),
                    "line_total": float(item.line_total),
                })

            sections_data.append({
                "name": section.name,
                "description": section.description,
                "line_items": line_items_data,
                "subtotal": float(section.subtotal),
            })

        return {
            "name": estimate.name,
            "sections": sections_data,
            "subtotal": float(estimate.subtotal),
            "tax_rate": float(estimate.tax_rate),
            "tax_amount": float(estimate.tax_amount),
            "total": float(estimate.total),
        }
