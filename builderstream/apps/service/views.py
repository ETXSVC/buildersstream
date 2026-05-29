"""Service & Warranty Management views."""
import logging

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationAdmin, IsOrganizationMember

from .models import ServiceAgreement, ServiceTicket, Warranty, WarrantyClaim
from .serializers import (
    AssignTicketSerializer,
    CompleteTicketSerializer,
    FileClaimSerializer,
    ResolveClaimSerializer,
    ServiceAgreementCreateSerializer,
    ServiceAgreementDetailSerializer,
    ServiceAgreementListSerializer,
    ServiceTicketCreateSerializer,
    ServiceTicketDetailSerializer,
    ServiceTicketListSerializer,
    WarrantyClaimCreateSerializer,
    WarrantyClaimDetailSerializer,
    WarrantyClaimListSerializer,
    WarrantyCreateSerializer,
    WarrantyDetailSerializer,
    WarrantyListSerializer,
)
from .services import ServiceAgreementService, ServiceTicketService, WarrantyService

User = get_user_model()
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# ServiceTicket
# --------------------------------------------------------------------------- #

class ServiceTicketViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = (
        ServiceTicket.objects
        .select_related("project", "client", "assigned_to", "invoice")
    )
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "priority", "ticket_type", "assigned_to", "billable"]
    search_fields = ["ticket_number", "title", "description"]
    ordering_fields = ["priority", "scheduled_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceTicketListSerializer
        if self.action == "create":
            return ServiceTicketCreateSerializer
        return ServiceTicketDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign a ticket to a technician."""
        ticket = self.get_object()
        ser = AssignTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        try:
            user = User.objects.get(pk=d["assigned_to"])
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = ServiceTicketService.assign_ticket(
            ticket, user, scheduled_date=d.get("scheduled_date")
        )
        return Response(ServiceTicketDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark a ticket as completed with resolution details."""
        ticket = self.get_object()
        ser = CompleteTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        try:
            updated = ServiceTicketService.complete_ticket(
                ticket,
                resolution=d["resolution"],
                labor_hours=d.get("labor_hours"),
                parts_cost=d.get("parts_cost"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ServiceTicketDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def generate_invoice(self, request, pk=None):
        """Generate a financials invoice for a completed, billable ticket."""
        ticket = self.get_object()
        try:
            invoice = ServiceTicketService.generate_invoice(ticket, request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": "Invoice created.", "invoice_id": str(invoice.pk)},
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------------------------------- #
# Warranty
# --------------------------------------------------------------------------- #

class WarrantyViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Warranty.objects.select_related("project")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "warranty_type", "status"]
    search_fields = ["description", "manufacturer"]
    ordering_fields = ["end_date", "start_date", "created_at"]
    ordering = ["end_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return WarrantyListSerializer
        if self.action == "create":
            return WarrantyCreateSerializer
        return WarrantyDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def file_claim(self, request, pk=None):
        """File a warranty claim against this warranty."""
        warranty = self.get_object()
        ser = FileClaimSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        service_ticket = None
        if d.get("service_ticket"):
            try:
                service_ticket = ServiceTicket.objects.get(
                    pk=d["service_ticket"],
                    organization=warranty.organization,
                )
            except ServiceTicket.DoesNotExist:
                return Response(
                    {"detail": "Service ticket not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            claim = WarrantyService.file_claim(
                warranty,
                description=d["description"],
                service_ticket=service_ticket,
                user=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            WarrantyClaimDetailSerializer(claim).data,
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------------------------------- #
# WarrantyClaim
# --------------------------------------------------------------------------- #

class WarrantyClaimViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = WarrantyClaim.objects.select_related("warranty", "service_ticket")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["warranty", "status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return WarrantyClaimListSerializer
        if self.action == "create":
            return WarrantyClaimCreateSerializer
        return WarrantyClaimDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Resolve a warranty claim."""
        claim = self.get_object()
        ser = ResolveClaimSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        try:
            updated = WarrantyService.resolve_claim(
                claim,
                resolution=d["resolution"],
                cost=d.get("cost"),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(WarrantyClaimDetailSerializer(updated).data)


# --------------------------------------------------------------------------- #
# ServiceAgreement
# --------------------------------------------------------------------------- #

class ServiceAgreementViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = ServiceAgreement.objects.select_related("client")
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["agreement_type", "status", "client", "auto_renew"]
    search_fields = ["name"]
    ordering_fields = ["end_date", "start_date", "created_at"]
    ordering = ["end_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ServiceAgreementListSerializer
        if self.action == "create":
            return ServiceAgreementCreateSerializer
        return ServiceAgreementDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def record_visit(self, request, pk=None):
        """Record a completed maintenance visit against the agreement."""
        agreement = self.get_object()
        updated = ServiceAgreementService.record_visit(agreement)
        return Response(ServiceAgreementDetailSerializer(updated).data)

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        """Renew the service agreement for another billing cycle."""
        agreement = self.get_object()
        updated = ServiceAgreementService.renew_agreement(agreement)
        return Response(ServiceAgreementDetailSerializer(updated).data)


# --------------------------------------------------------------------------- #
# Dispatch Board
# --------------------------------------------------------------------------- #

class DispatchBoardView(APIView):
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        """Return all tickets scheduled for a given date (default today) grouped by status."""
        from apps.tenants.context import get_current_organization
        from django.utils import timezone
        from .serializers import ServiceTicketListSerializer as TicketSer

        org = get_current_organization()
        if org is None:
            return Response(
                {"detail": "Organization context not resolved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        date_str = request.query_params.get("date")
        target_date = None
        if date_str:
            try:
                from datetime import date as date_cls
                target_date = date_cls.fromisoformat(date_str)
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        board, tickets = ServiceTicketService.get_dispatch_board(org, target_date)

        # Serialize the ticket lists inside by_status
        serialized_by_status = {}
        for st, tlist in board["by_status"].items():
            serialized_by_status[st] = TicketSer(tlist, many=True).data

        return Response({
            "date": board["date"],
            "total": board["total"],
            "by_status": serialized_by_status,
            "tickets": TicketSer(tickets, many=True).data,
        })
