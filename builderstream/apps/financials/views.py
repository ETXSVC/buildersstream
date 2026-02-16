"""Financial views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import Budget, ChangeOrder, Invoice
from .serializers import BudgetSerializer, ChangeOrderSerializer, InvoiceSerializer


class BudgetViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project"]


class InvoiceViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status"]
    search_fields = ["invoice_number"]


class ChangeOrderViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = ChangeOrder.objects.all()
    serializer_class = ChangeOrderSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status"]
    search_fields = ["number", "title"]
