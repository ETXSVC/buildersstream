"""Project views — CRUD, lifecycle actions, dashboard, action items, activity."""
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import (
    ActionItem,
    ActivityLog,
    DashboardLayout,
    Project,
    ProjectComment,
    ProjectMilestone,
    ProjectTeamMember,
)
from .serializers import (
    ActionItemSerializer,
    ActivityLogSerializer,
    DashboardLayoutSerializer,
    DashboardSerializer,
    MilestoneSerializer,
    ProjectCommentSerializer,
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectStatusTransitionSerializer,
    ProjectTeamMemberSerializer,
    StageTransitionLogSerializer,
)
from .services import DashboardService, ProjectLifecycleService


# ---------------------------------------------------------------------------
# 1. ProjectViewSet — CRUD + 4 custom actions
# ---------------------------------------------------------------------------

class ProjectViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Project.objects.select_related(
        "client", "project_manager", "organization",
    ).prefetch_related("team_members", "milestones")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "project_type", "is_active", "is_archived", "health_status"]
    search_fields = ["name", "project_number", "description", "city"]
    ordering_fields = ["name", "created_at", "start_date", "estimated_value", "health_score"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        if self.action == "create":
            return ProjectCreateSerializer
        return ProjectDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        org = getattr(self.request, "organization", None)
        if org:
            context["organization"] = org
        return context

    # -- Custom action: transition status ---------------------------------
    @action(detail=True, methods=["post"], url_path="transition-status")
    def transition_status(self, request, pk=None):
        project = self.get_object()
        serializer = ProjectStatusTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ProjectLifecycleService.transition_status(
                project=project,
                new_status=serializer.validated_data["new_status"],
                user=request.user,
                notes=serializer.validated_data.get("notes", ""),
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ProjectDetailSerializer(project, context=self.get_serializer_context()).data,
        )

    # -- Custom action: team members --------------------------------------
    @action(detail=True, methods=["get", "post", "delete"], url_path="team-members")
    def team_members(self, request, pk=None):
        project = self.get_object()

        if request.method == "GET":
            members = ProjectTeamMember.objects.filter(project=project).select_related("user")
            return Response(ProjectTeamMemberSerializer(members, many=True).data)

        if request.method == "POST":
            serializer = ProjectTeamMemberSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE — expects { "user": <user_id> }
        user_id = request.data.get("user")
        if not user_id:
            return Response(
                {"detail": "user field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted, _ = ProjectTeamMember.objects.filter(
            project=project, user_id=user_id,
        ).delete()
        if not deleted:
            return Response(
                {"detail": "Team member not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    # -- Custom action: milestones ----------------------------------------
    @action(detail=True, methods=["get", "post"], url_path="milestones")
    def milestones(self, request, pk=None):
        project = self.get_object()

        if request.method == "GET":
            qs = ProjectMilestone.objects.filter(project=project).order_by("sort_order")
            return Response(MilestoneSerializer(qs, many=True).data)

        serializer = MilestoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            project=project,
            organization=project.organization,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # -- Custom action: project activity ----------------------------------
    @action(detail=True, methods=["get"], url_path="activity")
    def activity(self, request, pk=None):
        project = self.get_object()
        qs = (
            ActivityLog.objects.filter(project=project)
            .select_related("user")
            .order_by("-created_at")[:50]
        )
        return Response(ActivityLogSerializer(qs, many=True).data)

    # -- Custom action: transition history --------------------------------
    @action(detail=True, methods=["get"], url_path="transitions")
    def transitions(self, request, pk=None):
        project = self.get_object()
        qs = project.stage_transitions.select_related("transitioned_by").order_by("-created_at")
        return Response(StageTransitionLogSerializer(qs, many=True).data)


# ---------------------------------------------------------------------------
# 2. DashboardView — cached org dashboard
# ---------------------------------------------------------------------------

class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        org = getattr(request, "organization", None)
        if not org:
            return Response(
                {"detail": "No organization context."},
                status=status.HTTP_403_FORBIDDEN,
            )
        data = DashboardService.get_dashboard_data(org, request.user)
        serializer = DashboardSerializer(data)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# 3. DashboardLayoutView — per-user widget layout
# ---------------------------------------------------------------------------

class DashboardLayoutView(generics.RetrieveUpdateAPIView):
    serializer_class = DashboardLayoutSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get_object(self):
        org = getattr(self.request, "organization", None)
        layout, _ = DashboardLayout.objects.get_or_create(
            user=self.request.user,
            organization=org,
            defaults={"layout": {}, "is_default": True},
        )
        return layout


# ---------------------------------------------------------------------------
# 4. ActionItemViewSet — CRUD with org scoping
# ---------------------------------------------------------------------------

class ActionItemViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ActionItemSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = [
        "item_type", "priority", "is_resolved",
        "assigned_to", "project",
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "priority", "created_at"]
    ordering = ["due_date", "-created_at"]

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        qs = ActionItem.objects.select_related("project", "assigned_to")
        if org:
            qs = qs.filter(organization=org)
        return qs

    def perform_create(self, serializer):
        org = getattr(self.request, "organization", None)
        serializer.save(organization=org)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.is_resolved and not instance.resolved_at:
            instance.resolved_at = timezone.now()
            instance.save(update_fields=["resolved_at"])


# ---------------------------------------------------------------------------
# 5. ActivityStreamView — paginated, read-only
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Kanban Board View — returns projects grouped by status
# ---------------------------------------------------------------------------

class KanbanBoardView(APIView):
    """
    GET /api/v1/projects/kanban/
    Returns projects grouped by lifecycle status, formatted for a kanban board.
    Each column contains: status, label, color, and list of project cards.
    """
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    STATUS_ORDER = [
        "prospect", "site_survey", "proposal", "acceptance",
        "in_progress", "milestones", "finish_project", "billing",
        "paid_complete", "canceled",
    ]

    STATUS_LABELS = {
        "prospect": "Prospect",
        "site_survey": "Site Survey",
        "proposal": "Proposal",
        "acceptance": "Acceptance",
        "in_progress": "In Progress",
        "milestones": "Milestones",
        "finish_project": "Finish Project",
        "billing": "Billing",
        "paid_complete": "Paid / Complete",
        "canceled": "Canceled",
    }

    STATUS_COLORS = {
        "prospect": "blue",
        "site_survey": "purple",
        "proposal": "indigo",
        "acceptance": "cyan",
        "in_progress": "amber",
        "milestones": "orange",
        "finish_project": "teal",
        "billing": "lime",
        "paid_complete": "green",
        "canceled": "red",
    }

    def get(self, request):
        org = getattr(request, "organization", None)
        if not org:
            return Response({"detail": "Organization required."}, status=400)

        # Optional filter: hide completed/canceled columns unless requested
        show_all = request.query_params.get("show_all", "false").lower() == "true"

        projects = (
            Project.objects.filter(organization=org)
            .select_related("client", "project_manager")
            .order_by("-updated_at")
        )

        # Group by status
        grouped: dict[str, list] = {s: [] for s in self.STATUS_ORDER}
        for project in projects:
            if project.status in grouped:
                grouped[project.status].append(self._card(project))

        columns = []
        for s in self.STATUS_ORDER:
            if not show_all and s in ("paid_complete", "canceled") and not grouped[s]:
                continue
            columns.append({
                "status": s,
                "label": self.STATUS_LABELS[s],
                "color": self.STATUS_COLORS[s],
                "count": len(grouped[s]),
                "projects": grouped[s],
            })

        return Response({"columns": columns})

    @staticmethod
    def _card(project):
        return {
            "id": str(project.id),
            "project_number": project.project_number,
            "name": project.name,
            "client_name": project.client_name,
            "project_manager_name": project.project_manager_name,
            "health_status": project.health_status,
            "health_score": project.health_score,
            "estimated_value": str(project.estimated_value) if project.estimated_value else None,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "estimated_completion": project.estimated_completion.isoformat() if project.estimated_completion else None,
            "updated_at": project.updated_at.isoformat(),
        }


class ActivityStreamView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ["action", "project", "user", "entity_type"]
    ordering = ["-created_at"]

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        qs = ActivityLog.objects.select_related("user", "project")
        if org:
            qs = qs.filter(organization=org)
        return qs


class ProjectCommentViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Threaded comments on a project.

    List returns only top-level comments (parent=None); replies nested inside.
    """

    serializer_class = ProjectCommentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        qs = (
            ProjectComment.objects.filter(parent__isnull=True, is_deleted=False)
            .select_related("author", "project")
            .prefetch_related("replies__author")
        )
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if org:
            qs = qs.filter(organization=org)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            organization=self.request.organization,
        )

    def perform_update(self, serializer):
        serializer.save(is_edited=True, edited_at=timezone.now())

    def perform_destroy(self, instance):
        # Soft-delete to preserve thread context
        instance.is_deleted = True
        instance.body = "[deleted]"
        instance.save(update_fields=["is_deleted", "body"])
