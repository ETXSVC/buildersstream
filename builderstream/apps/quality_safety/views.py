"""Quality and safety views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import Inspection, SafetyChecklist, SafetyIncident
from .serializers import InspectionSerializer, SafetyChecklistSerializer, SafetyIncidentSerializer


class InspectionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "inspection_type"]
    search_fields = ["title"]


class SafetyIncidentViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = SafetyIncident.objects.all()
    serializer_class = SafetyIncidentSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "severity", "is_osha_recordable", "is_resolved"]


class SafetyChecklistViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = SafetyChecklist.objects.all()
    serializer_class = SafetyChecklistSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["is_template"]
