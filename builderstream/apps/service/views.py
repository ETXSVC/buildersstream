"""Service views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import ServiceTicket, WarrantyItem
from .serializers import ServiceTicketSerializer, WarrantyItemSerializer


class ServiceTicketViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = ServiceTicket.objects.all()
    serializer_class = ServiceTicketSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "priority", "assigned_to"]
    search_fields = ["title", "description"]


class WarrantyItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = WarrantyItem.objects.all()
    serializer_class = WarrantyItemSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project"]
    search_fields = ["item_name"]
