"""Service & Warranty Management serializers."""
from rest_framework import serializers

from .models import ServiceAgreement, ServiceTicket, Warranty, WarrantyClaim


# --------------------------------------------------------------------------- #
# ServiceTicket
# --------------------------------------------------------------------------- #

class ServiceTicketListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceTicket
        fields = [
            "id", "ticket_number", "title", "priority", "status", "ticket_type",
            "project", "client", "client_name", "assigned_to", "assigned_to_name",
            "scheduled_date", "completed_date", "billable", "total_cost", "created_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None

    def get_client_name(self, obj):
        if obj.client:
            return str(obj.client)
        return None


class ServiceTicketDetailSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceTicket
        fields = [
            "id", "ticket_number", "title", "description", "priority", "status",
            "ticket_type", "project", "client", "client_name", "assigned_to",
            "assigned_to_name", "scheduled_date", "completed_date", "resolution",
            "billable", "billing_type", "labor_hours", "parts_cost", "total_cost",
            "invoice", "organization", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "ticket_number", "organization", "created_by", "created_at", "updated_at",
        ]

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None

    def get_client_name(self, obj):
        if obj.client:
            return str(obj.client)
        return None


class ServiceTicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTicket
        fields = [
            "title", "description", "priority", "ticket_type", "project", "client",
            "assigned_to", "scheduled_date", "billable", "billing_type",
        ]


class AssignTicketSerializer(serializers.Serializer):
    assigned_to = serializers.UUIDField()
    scheduled_date = serializers.DateTimeField(required=False, allow_null=True)


class CompleteTicketSerializer(serializers.Serializer):
    resolution = serializers.CharField()
    labor_hours = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    parts_cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


# --------------------------------------------------------------------------- #
# Warranty
# --------------------------------------------------------------------------- #

class WarrantyListSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Warranty
        fields = [
            "id", "warranty_type", "description", "start_date", "end_date",
            "status", "project", "project_name", "manufacturer", "is_active", "created_at",
        ]

    def get_project_name(self, obj):
        if obj.project:
            return obj.project.name
        return None


class WarrantyDetailSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    claims_count = serializers.SerializerMethodField()

    class Meta:
        model = Warranty
        fields = [
            "id", "warranty_type", "description", "coverage_details",
            "start_date", "end_date", "manufacturer", "product_info", "status",
            "project", "is_active", "claims_count",
            "organization", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]

    def get_claims_count(self, obj):
        return obj.claims.count()


class WarrantyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warranty
        fields = [
            "project", "warranty_type", "description", "coverage_details",
            "start_date", "end_date", "manufacturer", "product_info",
        ]


class FileClaimSerializer(serializers.Serializer):
    description = serializers.CharField()
    service_ticket = serializers.UUIDField(required=False, allow_null=True)


# --------------------------------------------------------------------------- #
# WarrantyClaim
# --------------------------------------------------------------------------- #

class WarrantyClaimListSerializer(serializers.ModelSerializer):
    warranty_description = serializers.SerializerMethodField()

    class Meta:
        model = WarrantyClaim
        fields = [
            "id", "warranty", "warranty_description", "service_ticket",
            "status", "cost", "created_at",
        ]

    def get_warranty_description(self, obj):
        return obj.warranty.description if obj.warranty_id else None


class WarrantyClaimDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyClaim
        fields = [
            "id", "warranty", "service_ticket", "description", "status",
            "cost", "resolution", "organization", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at"]


class WarrantyClaimCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyClaim
        fields = ["warranty", "service_ticket", "description"]


class ResolveClaimSerializer(serializers.Serializer):
    resolution = serializers.CharField()
    cost = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)


# --------------------------------------------------------------------------- #
# ServiceAgreement
# --------------------------------------------------------------------------- #

class ServiceAgreementListSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    visits_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = ServiceAgreement
        fields = [
            "id", "name", "agreement_type", "client", "client_name",
            "start_date", "end_date", "status", "billing_frequency", "billing_amount",
            "visits_per_year", "visits_completed", "visits_remaining", "auto_renew", "created_at",
        ]

    def get_client_name(self, obj):
        return str(obj.client) if obj.client_id else None


class ServiceAgreementDetailSerializer(serializers.ModelSerializer):
    visits_remaining = serializers.IntegerField(read_only=True)
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceAgreement
        fields = [
            "id", "name", "agreement_type", "client", "client_name",
            "start_date", "end_date", "billing_frequency", "billing_amount",
            "visits_per_year", "visits_completed", "visits_remaining",
            "auto_renew", "status", "notes",
            "organization", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "visits_completed", "organization", "created_by", "created_at", "updated_at",
        ]

    def get_client_name(self, obj):
        return str(obj.client) if obj.client_id else None


class ServiceAgreementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAgreement
        fields = [
            "name", "agreement_type", "client", "start_date", "end_date",
            "billing_frequency", "billing_amount", "visits_per_year", "auto_renew", "notes",
        ]
