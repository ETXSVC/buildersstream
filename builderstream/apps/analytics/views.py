"""Analytics & Reporting Engine views."""
import logging

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationAdmin, IsOrganizationMember

from .models import Dashboard, KPI, Report
from .serializers import (
    DashboardSerializer,
    KPICreateSerializer,
    KPIDetailSerializer,
    KPIListSerializer,
    ReportCreateSerializer,
    ReportDetailSerializer,
    ReportListSerializer,
)
from .services import ExportService, KPIService, ReportService

logger = logging.getLogger(__name__)


class DashboardViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsOrganizationMember]
    search_fields = ["name"]
    ordering = ["-is_default", "name"]

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        """Mark this dashboard as the default, unset all others."""
        dashboard = self.get_object()
        Dashboard.objects.filter(
            organization=dashboard.organization, is_default=True
        ).exclude(pk=dashboard.pk).update(is_default=False)
        dashboard.is_default = True
        dashboard.save(update_fields=["is_default", "updated_at"])
        return Response(DashboardSerializer(dashboard).data)


class ReportViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Report.objects.all()
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["report_type", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "last_run_at", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return ReportListSerializer
        if self.action == "create":
            return ReportCreateSerializer
        return ReportDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        """Execute the report and cache the result."""
        report = self.get_object()
        try:
            result = ReportService.run_report(report)
        except Exception as exc:
            logger.error("Report run failed: %s", exc)
            return Response(
                {"detail": f"Report execution failed: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"result": result})

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        """Download the last report result as CSV."""
        report = self.get_object()
        if not report.last_run_result:
            return Response(
                {"detail": "Run the report first."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        csv_bytes = ExportService.export_report_result_to_csv(report)
        filename = f"{report.name.replace(' ', '_')}.csv"
        response = HttpResponse(csv_bytes, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class KPIViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = KPI.objects.select_related("project")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "category"]
    search_fields = ["name"]
    ordering_fields = ["-period_end", "category", "name"]
    ordering = ["-period_end", "category", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return KPIListSerializer
        if self.action == "create":
            return KPICreateSerializer
        return KPIDetailSerializer

    def perform_create(self, serializer):
        serializer.save(organization_id=self.get_organization())

    @action(detail=False, methods=["post"])
    def calculate(self, request):
        """Trigger KPI calculation for the current org and current month."""
        from apps.tenants.context import get_current_organization

        org = get_current_organization()
        if org is None:
            return Response(
                {"detail": "Organization context not resolved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        kpis = KPIService.calculate_all_kpis(org)
        return Response({
            "kpis_updated": len(kpis),
            "detail": f"{len(kpis)} KPIs calculated.",
        })

    @action(detail=False, methods=["get"])
    def export(self, request):
        """Download KPIs as CSV."""
        from apps.tenants.context import get_current_organization

        org = get_current_organization()
        if org is None:
            return Response(
                {"detail": "Organization context not resolved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        category = request.query_params.get("category")
        csv_bytes = ExportService.export_kpis_to_csv(org, category=category)
        response = HttpResponse(csv_bytes, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="kpis.csv"'
        return response


class AnalyticsSummaryView(APIView):
    """Live org-wide analytics summary pulling from all modules."""
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        from apps.tenants.context import get_current_organization

        org = get_current_organization()
        if org is None:
            return Response(
                {"detail": "Organization context not resolved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            summary = KPIService.get_org_summary(org)
        except Exception as exc:
            logger.error("Analytics summary failed: %s", exc)
            return Response(
                {"detail": "Summary generation failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(summary)
