"""Estimating views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import CostCode, Estimate, EstimateLineItem
from .serializers import CostCodeSerializer, EstimateLineItemSerializer, EstimateSerializer


class CostCodeViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = CostCode.objects.all()
    serializer_class = CostCodeSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["category"]
    search_fields = ["code", "description"]


class EstimateViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Estimate.objects.all()
    serializer_class = EstimateSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status"]


class EstimateLineItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = EstimateLineItem.objects.all()
    serializer_class = EstimateLineItemSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["estimate"]
