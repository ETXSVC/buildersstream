"""Estimating views — ViewSets for all models + public proposal view."""
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

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
from .serializers import (
    AssemblyCreateSerializer,
    AssemblyDetailSerializer,
    AssemblyItemCreateSerializer,
    AssemblyItemSerializer,
    AssemblyListSerializer,
    CostCodeCreateSerializer,
    CostCodeDetailSerializer,
    CostCodeListSerializer,
    CostItemCreateSerializer,
    CostItemDetailSerializer,
    CostItemListSerializer,
    EstimateCreateSerializer,
    EstimateDetailSerializer,
    EstimateLineItemCreateSerializer,
    EstimateLineItemSerializer,
    EstimateListSerializer,
    EstimateSectionCreateSerializer,
    EstimateSectionSerializer,
    ProposalCreateSerializer,
    ProposalDetailSerializer,
    ProposalListSerializer,
    ProposalTemplateSerializer,
    PublicProposalSerializer,
)
from .services import (
    AssemblyService,
    EstimateCalculationService,
    ExportService,
    ProposalService,
)


# ============================================================================
# CostCode ViewSet
# ============================================================================

class CostCodeViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for cost codes (CSI MasterFormat)."""

    queryset = CostCode.objects.all()
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["division", "is_labor", "is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["division", "code", "name"]
    ordering = ["division", "code"]

    def get_serializer_class(self):
        if self.action == "list":
            return CostCodeListSerializer
        if self.action == "create":
            return CostCodeCreateSerializer
        return CostCodeDetailSerializer


# ============================================================================
# CostItem ViewSet
# ============================================================================

class CostItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for cost items with bulk import actions."""

    queryset = CostItem.objects.select_related("cost_code").all()
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["cost_code", "is_taxable", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "cost", "client_price"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return CostItemListSerializer
        if self.action == "create":
            return CostItemCreateSerializer
        return CostItemDetailSerializer

    @action(detail=False, methods=["get"], url_path="bulk-import-template")
    def bulk_import_template(self, request):
        """Download Excel template for bulk import."""
        # TODO: Generate Excel template with sample data
        return Response(
            {"detail": "Template generation not yet implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    @action(detail=False, methods=["post"], url_path="bulk-import")
    def bulk_import(self, request):
        """Upload Excel file to bulk create cost items."""
        # TODO: Parse Excel and create cost items
        return Response(
            {"detail": "Bulk import not yet implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


# ============================================================================
# Assembly ViewSet
# ============================================================================

class AssemblyViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for assemblies (grouped cost items)."""

    queryset = Assembly.objects.prefetch_related("assembly_items__cost_item").all()
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "total_cost", "total_price"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return AssemblyListSerializer
        if self.action == "create":
            return AssemblyCreateSerializer
        return AssemblyDetailSerializer

    @action(detail=True, methods=["post"])
    def copy(self, request, pk=None):
        """Copy assembly with all items."""
        assembly = self.get_object()

        # Create new assembly
        new_assembly = Assembly.objects.create(
            organization=assembly.organization,
            name=f"{assembly.name} (Copy)",
            description=assembly.description,
            notes=assembly.notes,
        )

        # Copy all assembly items
        for item in assembly.assembly_items.all():
            AssemblyItem.objects.create(
                organization=assembly.organization,
                assembly=new_assembly,
                cost_item=item.cost_item,
                quantity=item.quantity,
                sort_order=item.sort_order,
                notes=item.notes,
            )

        # Recalculate totals
        AssemblyService.calculate_assembly_totals(new_assembly)

        return Response(
            AssemblyDetailSerializer(new_assembly, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def calculate(self, request, pk=None):
        """Recalculate assembly totals."""
        assembly = self.get_object()
        AssemblyService.calculate_assembly_totals(assembly)

        return Response(
            AssemblyDetailSerializer(assembly, context=self.get_serializer_context()).data,
        )


# ============================================================================
# AssemblyItem ViewSet
# ============================================================================

class AssemblyItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for assembly items."""

    queryset = AssemblyItem.objects.select_related("assembly", "cost_item").all()
    serializer_class = AssemblyItemSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["assembly"]
    ordering_fields = ["sort_order"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.action == "create":
            return AssemblyItemCreateSerializer
        return AssemblyItemSerializer


# ============================================================================
# Estimate ViewSet
# ============================================================================

class EstimateViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for estimates with custom actions."""

    queryset = Estimate.objects.select_related(
        "project", "lead", "created_by", "approved_by"
    ).prefetch_related("sections__line_items").all()
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "project", "lead"]
    search_fields = ["name", "estimate_number", "notes"]
    ordering_fields = ["created_at", "estimate_number", "total"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return EstimateListSerializer
        if self.action == "create":
            return EstimateCreateSerializer
        return EstimateDetailSerializer

    def perform_create(self, serializer):
        """Auto-generate estimate number on creation."""
        # TODO: Implement auto-increment estimate number service
        estimate_number = f"EST-{timezone.now().year}-{Estimate.objects.filter(organization=self.request.organization).count() + 1:03d}"
        serializer.save(
            created_by=self.request.user,
            estimate_number=estimate_number,
        )

    @action(detail=True, methods=["post"])
    def copy(self, request, pk=None):
        """Copy estimate with all sections and line items."""
        estimate = self.get_object()
        new_name = request.data.get("name")

        new_estimate = EstimateCalculationService.copy_estimate(
            estimate=estimate,
            user=request.user,
            new_name=new_name,
        )

        return Response(
            EstimateDetailSerializer(new_estimate, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def recalculate(self, request, pk=None):
        """Recalculate all totals."""
        estimate = self.get_object()
        EstimateCalculationService.calculate_estimate_totals(estimate)

        return Response(
            EstimateDetailSerializer(estimate, context=self.get_serializer_context()).data,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve estimate."""
        estimate = self.get_object()
        estimate.status = "approved"
        estimate.approved_by = request.user
        estimate.approved_at = timezone.now()
        estimate.save()

        return Response(
            EstimateDetailSerializer(estimate, context=self.get_serializer_context()).data,
        )

    @action(detail=True, methods=["post"], url_path="generate-proposal")
    def generate_proposal(self, request, pk=None):
        """Create proposal from estimate."""
        estimate = self.get_object()

        client_id = request.data.get("client_id")
        if not client_id:
            return Response(
                {"detail": "client_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.crm.models import Contact
        try:
            client = Contact.objects.get(pk=client_id, organization=request.organization)
        except Contact.DoesNotExist:
            return Response(
                {"detail": "Client not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        proposal = ProposalService.generate_proposal_from_estimate(
            estimate=estimate,
            user=request.user,
            client=client,
        )

        return Response(
            ProposalDetailSerializer(proposal, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="export-excel")
    def export_excel(self, request, pk=None):
        """Download Excel export."""
        estimate = self.get_object()
        excel_file = ExportService.export_estimate_to_excel(estimate)

        response = HttpResponse(
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="estimate_{estimate.estimate_number}.xlsx"'
        return response


# ============================================================================
# EstimateSection ViewSet
# ============================================================================

class EstimateSectionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for estimate sections."""

    queryset = EstimateSection.objects.select_related("estimate").prefetch_related("line_items").all()
    serializer_class = EstimateSectionSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["estimate"]
    ordering_fields = ["sort_order"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.action == "create":
            return EstimateSectionCreateSerializer
        return EstimateSectionSerializer

    @action(detail=True, methods=["post"])
    def reorder(self, request, pk=None):
        """Update sort_order for section."""
        section = self.get_object()
        new_order = request.data.get("sort_order")

        if new_order is None:
            return Response(
                {"detail": "sort_order is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        section.sort_order = new_order
        section.save()

        return Response(
            EstimateSectionSerializer(section, context=self.get_serializer_context()).data,
        )


# ============================================================================
# EstimateLineItem ViewSet
# ============================================================================

class EstimateLineItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for estimate line items."""

    queryset = EstimateLineItem.objects.select_related(
        "section", "cost_item", "assembly"
    ).all()
    serializer_class = EstimateLineItemSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["section", "cost_item", "assembly", "is_taxable"]
    ordering_fields = ["sort_order"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.action == "create":
            return EstimateLineItemCreateSerializer
        return EstimateLineItemSerializer

    @action(detail=True, methods=["post"])
    def reorder(self, request, pk=None):
        """Update sort_order for line item."""
        line_item = self.get_object()
        new_order = request.data.get("sort_order")

        if new_order is None:
            return Response(
                {"detail": "sort_order is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        line_item.sort_order = new_order
        line_item.save()

        return Response(
            EstimateLineItemSerializer(line_item, context=self.get_serializer_context()).data,
        )


# ============================================================================
# Proposal ViewSet
# ============================================================================

class ProposalViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for proposals with custom actions."""

    queryset = Proposal.objects.select_related(
        "estimate", "client", "template"
    ).all()
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "client", "is_signed"]
    search_fields = ["proposal_number", "sent_to_email"]
    ordering_fields = ["sent_at", "created_at"]
    ordering = ["-sent_at", "-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProposalListSerializer
        if self.action == "create":
            return ProposalCreateSerializer
        return ProposalDetailSerializer

    def perform_create(self, serializer):
        """Auto-generate proposal number on creation."""
        # TODO: Implement auto-increment proposal number service
        proposal_number = f"PROP-{timezone.now().year}-{Proposal.objects.filter(organization=self.request.organization).count() + 1:03d}"
        serializer.save(proposal_number=proposal_number)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        """Send proposal via email."""
        proposal = self.get_object()
        recipient_email = request.data.get("recipient_email")

        ProposalService.send_proposal(
            proposal=proposal,
            user=request.user,
            recipient_email=recipient_email,
        )

        return Response(
            ProposalDetailSerializer(proposal, context=self.get_serializer_context()).data,
        )

    @action(detail=True, methods=["post"], url_path="regenerate-pdf")
    def regenerate_pdf(self, request, pk=None):
        """Regenerate PDF from current estimate."""
        proposal = self.get_object()

        from .tasks import generate_pdf_proposal
        generate_pdf_proposal.delay(str(proposal.pk))

        return Response(
            {"detail": "PDF generation queued"},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        """Preview proposal without sending."""
        proposal = self.get_object()
        return Response(
            ProposalDetailSerializer(proposal, context=self.get_serializer_context()).data,
        )


# ============================================================================
# ProposalTemplate ViewSet
# ============================================================================

class ProposalTemplateViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for proposal templates."""

    queryset = ProposalTemplate.objects.all()
    serializer_class = ProposalTemplateSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["is_default"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"], url_path="set-default")
    def set_default(self, request, pk=None):
        """Set as default template (unset others)."""
        template = self.get_object()

        # Unset all other defaults
        ProposalTemplate.objects.filter(
            organization=request.organization,
            is_default=True,
        ).update(is_default=False)

        # Set this one as default
        template.is_default = True
        template.save()

        return Response(
            ProposalTemplateSerializer(template, context=self.get_serializer_context()).data,
        )


# ============================================================================
# Public Proposal View (Unauthenticated)
# ============================================================================

class PublicProposalView(APIView):
    """Public view for proposal viewing and signing (no auth required)."""

    permission_classes = [AllowAny]

    def get(self, request, public_token):
        """Get proposal by public token."""
        try:
            proposal = Proposal.objects.select_related(
                "estimate", "client", "organization"
            ).prefetch_related(
                "estimate__sections__line_items"
            ).get(public_token=public_token)
        except Proposal.DoesNotExist:
            return Response(
                {"detail": "Proposal not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Increment view count on first view
        if not proposal.viewed_at:
            proposal.viewed_at = timezone.now()
            proposal.view_count = 1
            proposal.status = "viewed"
        else:
            proposal.view_count += 1
        proposal.save()

        return Response(PublicProposalSerializer(proposal).data)

    def post(self, request, public_token):
        """Capture e-signature."""
        try:
            proposal = Proposal.objects.get(public_token=public_token)
        except Proposal.DoesNotExist:
            return Response(
                {"detail": "Proposal not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Validate required fields
        signature_data = request.data.get("signature_data")
        signed_by_name = request.data.get("signed_by_name")

        if not signature_data or not signed_by_name:
            return Response(
                {"detail": "signature_data and signed_by_name are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Capture signature
        try:
            ip_address = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            ProposalService.capture_signature(
                proposal=proposal,
                signature_data=signature_data,
                signed_by_name=signed_by_name,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return Response(
                PublicProposalSerializer(proposal).data,
                status=status.HTTP_200_OK,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
