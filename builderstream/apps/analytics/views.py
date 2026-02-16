"""Analytics views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import Dashboard, KPI, Report
from .serializers import DashboardSerializer, KPISerializer, ReportSerializer


class DashboardViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsOrganizationMember]


class ReportViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["report_type", "is_active"]


class KPIViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "category"]
