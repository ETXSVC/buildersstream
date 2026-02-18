"""Financial Management Suite — ViewSets and report views."""
import logging
from datetime import date

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember, role_required
from apps.tenants.context import get_current_organization

from .models import (
    Budget,
    ChangeOrder,
    ChangeOrderLineItem,
    CostCode,
    Expense,
    Invoice,
    InvoiceLineItem,
    Payment,
    PurchaseOrder,
    PurchaseOrderLineItem,
)
from .serializers import (
    BudgetListSerializer,
    BudgetSerializer,
    ChangeOrderCreateSerializer,
    ChangeOrderLineItemCreateSerializer,
    ChangeOrderLineItemSerializer,
    ChangeOrderListSerializer,
    ChangeOrderSerializer,
    CostCodeListSerializer,
    CostCodeSerializer,
    ExpenseCreateSerializer,
    ExpenseListSerializer,
    ExpenseSerializer,
    InvoiceCreateSerializer,
    InvoiceLineItemCreateSerializer,
    InvoiceLineItemSerializer,
    InvoiceListSerializer,
    InvoiceSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
    PurchaseOrderCreateSerializer,
    PurchaseOrderLineItemCreateSerializer,
    PurchaseOrderLineItemSerializer,
    PurchaseOrderListSerializer,
    PurchaseOrderSerializer,
)
from .services import (
    ChangeOrderService,
    InvoicingService,
    JobCostingService,
    PurchaseOrderService,
)

logger = logging.getLogger(__name__)


class CostCodeViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for cost codes (CSI MasterFormat classification)."""

    queryset = CostCode.objects.all()
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["division", "is_labor", "is_active"]
    search_fields = ["code", "name"]
    ordering_fields = ["division", "code", "name"]
    ordering = ["division", "code"]

    def get_serializer_class(self):
        if self.action == "list":
            return CostCodeListSerializer
        return CostCodeSerializer


class BudgetViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for project budget lines."""

    queryset = Budget.objects.select_related("project", "cost_code")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "budget_type", "cost_code"]
    ordering = ["project", "cost_code"]

    def get_serializer_class(self):
        if self.action == "list":
            return BudgetListSerializer
        return BudgetSerializer

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """GET /budgets/summary/?project_id=<uuid> — job cost summary."""
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response({"detail": "project_id query param required."}, status=400)

        from apps.projects.models import Project
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        data = JobCostingService.get_project_cost_summary(project)
        return Response(data)

    @action(detail=False, methods=["post"], url_path="sync-actuals")
    def sync_actuals(self, request):
        """POST /budgets/sync-actuals/?project_id=<uuid> — sync expense actuals to budget lines."""
        project_id = request.data.get("project_id") or request.query_params.get("project_id")
        if not project_id:
            return Response({"detail": "project_id required."}, status=400)

        from apps.projects.models import Project
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        JobCostingService.update_budget_actuals(project)
        return Response({"detail": "Budget actuals synced."})


class ExpenseViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for project expenses with approval workflow."""

    queryset = Expense.objects.select_related("project", "cost_code", "submitted_by", "approved_by")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "expense_type", "approval_status", "cost_code"]
    search_fields = ["description", "vendor_name"]
    ordering_fields = ["expense_date", "amount", "approval_status"]
    ordering = ["-expense_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ExpenseListSerializer
        if self.action == "create":
            return ExpenseCreateSerializer
        return ExpenseSerializer

    def perform_create(self, serializer):
        org_id = self.get_organization()
        serializer.save(
            organization_id=org_id,
            submitted_by=self.request.user,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """POST /expenses/{pk}/approve/ — approve an expense."""
        expense = self.get_object()
        expense.approval_status = "approved"
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.save(update_fields=["approval_status", "approved_by", "approved_at", "updated_at"])

        # Sync actuals on the related budget line
        if expense.budget_line:
            JobCostingService.update_budget_actuals(expense.project)

        return Response(ExpenseSerializer(expense, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """POST /expenses/{pk}/reject/ — reject an expense."""
        expense = self.get_object()
        expense.approval_status = "rejected"
        expense.save(update_fields=["approval_status", "updated_at"])
        return Response(ExpenseSerializer(expense, context=self.get_serializer_context()).data)


class InvoiceViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for client invoices."""

    queryset = Invoice.objects.select_related("project", "client", "created_by").prefetch_related("line_items")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "invoice_type", "client"]
    search_fields = ["invoice_number", "sent_to_email"]
    ordering_fields = ["issue_date", "due_date", "total", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        if self.action == "create":
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        org_id = self.get_organization()
        from apps.tenants.models import Organization
        org = Organization.objects.get(pk=org_id)
        invoice_number = InvoicingService.generate_invoice_number(org)
        serializer.save(
            organization_id=org_id,
            invoice_number=invoice_number,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="send")
    def send_invoice(self, request, pk=None):
        """POST /invoices/{pk}/send/ — mark invoice as sent."""
        invoice = self.get_object()
        recipient = request.data.get("email") or invoice.sent_to_email
        if not recipient and invoice.client:
            recipient = invoice.client.email or ""
        InvoicingService.mark_sent(invoice, recipient, user=request.user)
        return Response(InvoiceSerializer(invoice, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="record-payment")
    def record_payment(self, request, pk=None):
        """POST /invoices/{pk}/record-payment/ — record a payment against an invoice."""
        invoice = self.get_object()
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = InvoicingService.record_payment(
            invoice=invoice,
            amount=serializer.validated_data["amount"],
            payment_date=serializer.validated_data["payment_date"],
            payment_method=serializer.validated_data.get("payment_method", "check"),
            reference_number=serializer.validated_data.get("reference_number", ""),
            notes=serializer.validated_data.get("notes", ""),
            recorded_by=request.user,
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="recalculate")
    def recalculate(self, request, pk=None):
        """POST /invoices/{pk}/recalculate/ — recalculate totals from line items."""
        invoice = self.get_object()
        InvoicingService.recalculate_invoice(invoice)
        return Response(InvoiceSerializer(invoice, context=self.get_serializer_context()).data)


class InvoiceLineItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for invoice line items."""

    queryset = InvoiceLineItem.objects.select_related("invoice", "cost_code")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["invoice"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.action == "create":
            return InvoiceLineItemCreateSerializer
        return InvoiceLineItemSerializer

    def get_queryset(self):
        # Filter by invoices belonging to the org
        org_id = self.get_organization()
        return InvoiceLineItem.objects.filter(invoice__organization_id=org_id).select_related("invoice", "cost_code")

    def perform_create(self, serializer):
        instance = serializer.save()
        # Recalculate invoice totals after adding line item
        InvoicingService.recalculate_invoice(instance.invoice)

    def perform_destroy(self, instance):
        invoice = instance.invoice
        instance.delete()
        InvoicingService.recalculate_invoice(invoice)


class PaymentViewSet(TenantViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for payments (create via InvoiceViewSet.record_payment)."""

    queryset = Payment.objects.select_related("invoice", "project", "recorded_by")
    serializer_class = PaymentSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["invoice", "project", "payment_method"]
    ordering = ["-payment_date"]


class ChangeOrderViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for change orders."""

    queryset = ChangeOrder.objects.select_related("project", "client", "created_by").prefetch_related("line_items")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "client"]
    search_fields = ["title", "description"]
    ordering_fields = ["number", "cost_impact", "submitted_date", "status"]
    ordering = ["project", "number"]

    def get_serializer_class(self):
        if self.action == "list":
            return ChangeOrderListSerializer
        if self.action == "create":
            return ChangeOrderCreateSerializer
        return ChangeOrderSerializer

    def perform_create(self, serializer):
        org_id = self.get_organization()
        project = serializer.validated_data["project"]
        number = ChangeOrderService.get_next_co_number(project)
        serializer.save(
            organization_id=org_id,
            number=number,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        """POST /change-orders/{pk}/submit/ — submit CO to client."""
        co = self.get_object()
        ChangeOrderService.submit_change_order(co, request.user)
        return Response(ChangeOrderSerializer(co, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """POST /change-orders/{pk}/approve/ — approve CO and update project value."""
        co = self.get_object()
        approved_by_name = request.data.get("approved_by_name", "")
        ChangeOrderService.approve_change_order(co, approved_by_name, request.user)
        return Response(ChangeOrderSerializer(co, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """POST /change-orders/{pk}/reject/ — reject CO."""
        co = self.get_object()
        reason = request.data.get("reason", "")
        ChangeOrderService.reject_change_order(co, reason, request.user)
        return Response(ChangeOrderSerializer(co, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="recalculate")
    def recalculate(self, request, pk=None):
        """POST /change-orders/{pk}/recalculate/ — recalculate cost_impact from line items."""
        co = self.get_object()
        ChangeOrderService.recalculate_cost_impact(co)
        return Response(ChangeOrderSerializer(co, context=self.get_serializer_context()).data)


class ChangeOrderLineItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for change order line items."""

    queryset = ChangeOrderLineItem.objects.select_related("change_order", "cost_code")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["change_order"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.action == "create":
            return ChangeOrderLineItemCreateSerializer
        return ChangeOrderLineItemSerializer

    def get_queryset(self):
        org_id = self.get_organization()
        return ChangeOrderLineItem.objects.filter(
            change_order__organization_id=org_id
        ).select_related("change_order", "cost_code")

    def perform_create(self, serializer):
        instance = serializer.save()
        ChangeOrderService.recalculate_cost_impact(instance.change_order)

    def perform_destroy(self, instance):
        co = instance.change_order
        instance.delete()
        ChangeOrderService.recalculate_cost_impact(co)


class PurchaseOrderViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for purchase orders."""

    queryset = PurchaseOrder.objects.select_related("project", "created_by").prefetch_related("line_items")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "vendor_name"]
    search_fields = ["po_number", "vendor_name"]
    ordering_fields = ["po_number", "issue_date", "total", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return PurchaseOrderListSerializer
        if self.action == "create":
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        org_id = self.get_organization()
        from apps.tenants.models import Organization
        org = Organization.objects.get(pk=org_id)
        po_number = PurchaseOrderService.generate_po_number(org)
        serializer.save(
            organization_id=org_id,
            po_number=po_number,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="receive")
    def receive(self, request, pk=None):
        """POST /purchase-orders/{pk}/receive/ — record received quantities per line item.

        Body: { "line_items": { "<line_item_id>": <quantity>, ... } }
        """
        po = self.get_object()
        received = request.data.get("line_items", {})
        PurchaseOrderService.receive_line_items(po, received, user=request.user)
        return Response(PurchaseOrderSerializer(po, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["post"], url_path="recalculate")
    def recalculate(self, request, pk=None):
        """POST /purchase-orders/{pk}/recalculate/ — recalculate totals from line items."""
        po = self.get_object()
        PurchaseOrderService.recalculate_po_totals(po)
        return Response(PurchaseOrderSerializer(po, context=self.get_serializer_context()).data)


class PurchaseOrderLineItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for PO line items."""

    queryset = PurchaseOrderLineItem.objects.select_related("purchase_order", "cost_code")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["purchase_order"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.action == "create":
            return PurchaseOrderLineItemCreateSerializer
        return PurchaseOrderLineItemSerializer

    def get_queryset(self):
        org_id = self.get_organization()
        return PurchaseOrderLineItem.objects.filter(
            purchase_order__organization_id=org_id
        ).select_related("purchase_order", "cost_code")

    def perform_create(self, serializer):
        instance = serializer.save()
        PurchaseOrderService.recalculate_po_totals(instance.purchase_order)

    def perform_destroy(self, instance):
        po = instance.purchase_order
        instance.delete()
        PurchaseOrderService.recalculate_po_totals(po)


# ─────────────────────────────────────────────────────────────────────────── #
#  Report Views                                                               #
# ─────────────────────────────────────────────────────────────────────────── #

class JobCostReportView(APIView):
    """GET /financials/reports/job-cost/?project_id=<uuid>

    Returns a full job cost summary comparing budgeted vs actual amounts
    across all cost codes for a single project.
    """

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response({"detail": "project_id query param required."}, status=400)

        from apps.projects.models import Project
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        data = JobCostingService.get_project_cost_summary(project)
        return Response(data)


class CashFlowForecastView(APIView):
    """GET /financials/reports/cash-flow/?months=6

    Returns a month-by-month cash flow forecast for the organization.
    """

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        try:
            months = int(request.query_params.get("months", 6))
            months = max(1, min(months, 24))
        except (ValueError, TypeError):
            months = 6

        org = get_current_organization()
        if not org:
            return Response({"detail": "No organization context."}, status=400)

        data = JobCostingService.get_cash_flow_forecast(org, months=months)
        return Response({"months": months, "forecast": data})
