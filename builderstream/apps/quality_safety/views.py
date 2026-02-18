"""Quality & Safety views."""
import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember, role_required
from apps.tenants.context import get_current_organization

from .models import (
    Deficiency,
    Inspection,
    InspectionChecklist,
    SafetyIncident,
    ToolboxTalk,
)
from .serializers import (
    CloseIncidentSerializer,
    DeficiencyCreateSerializer,
    DeficiencyDetailSerializer,
    DeficiencyListSerializer,
    InspectionChecklistCreateSerializer,
    InspectionChecklistDetailSerializer,
    InspectionChecklistListSerializer,
    InspectionCreateSerializer,
    InspectionDetailSerializer,
    InspectionListSerializer,
    RecordResultsSerializer,
    ResolveDeficiencySerializer,
    SafetyIncidentCreateSerializer,
    SafetyIncidentDetailSerializer,
    SafetyIncidentListSerializer,
    ToolboxTalkCreateSerializer,
    ToolboxTalkDetailSerializer,
    ToolboxTalkListSerializer,
)
from .services import (
    DeficiencyService,
    InspectionService,
    QualityAnalyticsService,
    SafetyService,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# InspectionChecklist
# ---------------------------------------------------------------------------

class InspectionChecklistViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Inspection checklist templates."""

    queryset = InspectionChecklist.objects.prefetch_related("items")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["checklist_type", "category", "is_template", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "category", "created_at"]
    ordering = ["category", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return InspectionChecklistListSerializer
        if self.action in ("create", "update", "partial_update"):
            return InspectionChecklistCreateSerializer
        return InspectionChecklistDetailSerializer


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------

class InspectionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Inspection instances tied to projects."""

    queryset = Inspection.objects.select_related(
        "project", "checklist", "inspector"
    ).prefetch_related("results", "deficiencies")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "checklist", "checklist__checklist_type", "checklist__category"]
    search_fields = ["checklist__name", "notes", "project__name"]
    ordering_fields = ["inspection_date", "status", "overall_score", "created_at"]
    ordering = ["-inspection_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return InspectionListSerializer
        if self.action == "create":
            return InspectionCreateSerializer
        return InspectionDetailSerializer

    def perform_create(self, serializer):
        """Create inspection and seed InspectionResult rows from checklist."""
        org = self.request.organization
        checklist = serializer.validated_data["checklist"]
        project = serializer.validated_data["project"]
        inspector = serializer.validated_data.get("inspector")
        inspection_date = serializer.validated_data.get("inspection_date")
        inspection = InspectionService.create_from_checklist(
            checklist=checklist,
            project=project,
            organization=org,
            inspector=inspector,
            inspection_date=inspection_date,
        )
        return inspection

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = self.perform_create(serializer)
        out = InspectionDetailSerializer(inspection, context=self.get_serializer_context())
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"])
    def record_results(self, request, pk=None):
        """Bulk-record inspection results and recalculate score."""
        inspection = self.get_object()
        serializer = RecordResultsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results_data = serializer.validated_data["results"]
        final_status = serializer.validated_data.get("final_status")
        notes = serializer.validated_data.get("notes", "")

        try:
            inspection = InspectionService.record_results(inspection, results_data)
            if final_status:
                inspection = InspectionService.complete_inspection(
                    inspection, final_status, notes=notes
                )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            InspectionDetailSerializer(inspection, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Finalize an inspection with a pass/fail/conditional status."""
        inspection = self.get_object()
        final_status = request.data.get("final_status")
        notes = request.data.get("notes", "")
        if not final_status:
            return Response(
                {"detail": "final_status is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            inspection = InspectionService.complete_inspection(
                inspection, final_status, notes=notes
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            InspectionDetailSerializer(inspection, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=["get"])
    def report(self, request, pk=None):
        """Return a structured data report for this inspection."""
        inspection = self.get_object()
        return Response(InspectionService.generate_report(inspection))


# ---------------------------------------------------------------------------
# Deficiency
# ---------------------------------------------------------------------------

class DeficiencyViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Quality deficiencies and punch-list items."""

    queryset = Deficiency.objects.select_related(
        "project", "inspection", "assigned_to", "resolved_by", "verified_by"
    )
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "severity", "inspection", "assigned_to"]
    search_fields = ["title", "description", "resolution_notes"]
    ordering_fields = ["severity", "status", "due_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return DeficiencyListSerializer
        if self.action == "create":
            return DeficiencyCreateSerializer
        return DeficiencyDetailSerializer

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Mark a deficiency as resolved."""
        deficiency = self.get_object()
        serializer = ResolveDeficiencySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            deficiency = DeficiencyService.resolve(
                deficiency,
                notes=serializer.validated_data["notes"],
                resolved_by=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            DeficiencyDetailSerializer(deficiency, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Verify a resolved deficiency."""
        deficiency = self.get_object()
        try:
            deficiency = DeficiencyService.verify(deficiency, verifier=request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            DeficiencyDetailSerializer(deficiency, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        """Reopen a resolved/verified deficiency back to in-progress."""
        deficiency = self.get_object()
        notes = request.data.get("notes", "")
        try:
            deficiency = DeficiencyService.reopen(deficiency, user=request.user, notes=notes)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            DeficiencyDetailSerializer(deficiency, context=self.get_serializer_context()).data
        )


# ---------------------------------------------------------------------------
# SafetyIncident
# ---------------------------------------------------------------------------

class SafetyIncidentViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Safety incident reports."""

    queryset = SafetyIncident.objects.select_related("project", "reported_by")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "severity", "incident_type", "osha_reportable", "status"]
    search_fields = ["description", "root_cause", "corrective_actions", "injured_person_name"]
    ordering_fields = ["incident_date", "severity", "status", "created_at"]
    ordering = ["-incident_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return SafetyIncidentListSerializer
        if self.action == "create":
            return SafetyIncidentCreateSerializer
        return SafetyIncidentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.organization,
            reported_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def advance_status(self, request, pk=None):
        """Advance incident to the next status stage."""
        incident = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"detail": "status field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            incident = SafetyService.advance_status(incident, new_status)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            SafetyIncidentDetailSerializer(incident, context=self.get_serializer_context()).data
        )

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Close an incident with optional corrective action notes."""
        incident = self.get_object()
        serializer = CloseIncidentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            incident = SafetyService.close_incident(
                incident,
                corrective_notes=serializer.validated_data.get("corrective_notes", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            SafetyIncidentDetailSerializer(incident, context=self.get_serializer_context()).data
        )


# ---------------------------------------------------------------------------
# ToolboxTalk
# ---------------------------------------------------------------------------

class ToolboxTalkViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Toolbox talk / safety meeting records."""

    queryset = ToolboxTalk.objects.select_related("project", "presented_by").prefetch_related("attendees")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "presented_by"]
    search_fields = ["topic", "content"]
    ordering_fields = ["presented_date", "topic", "created_at"]
    ordering = ["-presented_date"]

    def get_serializer_class(self):
        if self.action == "list":
            return ToolboxTalkListSerializer
        if self.action == "create":
            return ToolboxTalkCreateSerializer
        return ToolboxTalkDetailSerializer


# ---------------------------------------------------------------------------
# Analytics views
# ---------------------------------------------------------------------------

class QualityScoresView(APIView):
    """GET /quality-safety/analytics/quality-scores/?project_id=..."""
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response(
                {"detail": "project_id query param required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from apps.projects.models import Project
            project = Project.objects.get(pk=project_id, organization=request.organization)
        except Exception:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        data = QualityAnalyticsService.get_quality_scores(project, request.organization)
        return Response(data)


class IncidentTrendsView(APIView):
    """GET /quality-safety/analytics/incident-trends/?months=6"""
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        try:
            months = int(request.query_params.get("months", 6))
            months = max(1, min(months, 24))
        except ValueError:
            months = 6

        data = QualityAnalyticsService.get_incident_trends(request.organization, months=months)
        return Response(data)


class DeficiencyStatsView(APIView):
    """GET /quality-safety/analytics/deficiency-stats/?project_id=..."""
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        project = None
        project_id = request.query_params.get("project_id")
        if project_id:
            try:
                from apps.projects.models import Project
                project = Project.objects.get(pk=project_id, organization=request.organization)
            except Exception:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        data = QualityAnalyticsService.get_deficiency_stats(request.organization, project=project)
        return Response(data)


class SafetySummaryView(APIView):
    """GET /quality-safety/analytics/safety-summary/?project_id=..."""
    permission_classes = [IsOrganizationMember]

    def get(self, request):
        project = None
        project_id = request.query_params.get("project_id")
        if project_id:
            try:
                from apps.projects.models import Project
                project = Project.objects.get(pk=project_id, organization=request.organization)
            except Exception:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        data = QualityAnalyticsService.get_safety_summary(request.organization, project=project)
        return Response(data)
