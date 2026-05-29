"""Issue Tracking views — ViewSets and SLA report."""
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember, IsOrganizationAdmin

from .models import CannedResponse, EscalationRule, Issue, IssueAttachment, IssueComment, IssueType
from .serializers import (
    CannedResponseSerializer,
    EscalationRuleSerializer,
    IssueAttachmentSerializer,
    IssueCommentSerializer,
    IssueCreateSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    IssueTypeSerializer,
    SLAComplianceSerializer,
)
from .services import SLAComplianceReport, SLAService


class IssueTypeViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Issue type management."""

    queryset = IssueType.objects.all()
    serializer_class = IssueTypeSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering = ["name"]


class IssueViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Issue management with SLA tracking and status transitions."""

    queryset = Issue.objects.select_related(
        "issue_type", "project", "client", "assignee", "reporter"
    )
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["status", "priority", "issue_type", "assignee", "project"]
    search_fields = ["number", "title", "description", "tags"]
    ordering_fields = ["created_at", "priority", "sla_resolution_due_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return IssueListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return IssueCreateSerializer
        return IssueDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["organization"] = getattr(self.request, "organization", None)
        return ctx

    @action(detail=True, methods=["post"], url_path="transition")
    def transition_status(self, request, pk=None):
        """Transition issue to a new status."""
        issue = self.get_object()
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "status required"}, status=status.HTTP_400_BAD_REQUEST)

        valid = [s[0] for s in Issue.Status.choices]
        if new_status not in valid:
            return Response(
                {"error": f"Invalid status. Valid: {valid}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = issue.status
        issue.status = new_status
        issue.save(update_fields=["status"])

        # Mark resolution SLA
        if new_status in (Issue.Status.RESOLVED, Issue.Status.CLOSED):
            SLAService.mark_resolution(issue)

        return Response(
            {
                "message": f"Status changed from '{old_status}' to '{new_status}'",
                "issue": IssueDetailSerializer(issue).data,
            }
        )

    @action(detail=True, methods=["post"], url_path="add-comment")
    def add_comment(self, request, pk=None):
        """Add a comment to this issue."""
        issue = self.get_object()
        serializer = IssueCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = IssueComment.objects.create(
            organization=issue.organization,
            issue=issue,
            content=serializer.validated_data["content"],
            parent=serializer.validated_data.get("parent"),
            is_internal=serializer.validated_data.get("is_internal", False),
            created_by=request.user,
        )

        # Mark first response SLA
        if not issue.first_responded_at and request.user != issue.reporter:
            SLAService.mark_response_met(issue)

        return Response(
            IssueCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="comments")
    def list_comments(self, request, pk=None):
        """List comments for this issue."""
        issue = self.get_object()
        comments = issue.comments.filter(parent__isnull=True).order_by("created_at")
        return Response(IssueCommentSerializer(comments, many=True).data)

    @action(detail=True, methods=["post"], url_path="attach")
    def add_attachment(self, request, pk=None):
        """Attach a file to this issue."""
        issue = self.get_object()
        serializer = IssueAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment = IssueAttachment.objects.create(
            organization=issue.organization,
            issue=issue,
            file_key=serializer.validated_data["file_key"],
            filename=serializer.validated_data["filename"],
            file_size=serializer.validated_data.get("file_size", 0),
            content_type=serializer.validated_data.get("content_type", ""),
            uploaded_by=request.user,
        )
        return Response(
            IssueAttachmentSerializer(attachment).data,
            status=status.HTTP_201_CREATED,
        )


class IssueCommentViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Comment management."""

    queryset = IssueComment.objects.select_related("created_by", "issue")
    serializer_class = IssueCommentSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["issue", "parent", "is_internal"]
    ordering = ["created_at"]

    def perform_update(self, serializer):
        serializer.save(is_edited=True, edited_at=timezone.now())


class CannedResponseViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Canned response template management."""

    queryset = CannedResponse.objects.select_related("issue_type")
    serializer_class = CannedResponseSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["issue_type", "is_active"]
    search_fields = ["name", "content"]
    ordering = ["name"]


class EscalationRuleViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Escalation rule management (admin only)."""

    queryset = EscalationRule.objects.all()
    serializer_class = EscalationRuleSerializer
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["is_active", "action_type"]
    ordering = ["name"]


class SLAComplianceView(APIView):
    """SLA compliance report for the organization."""

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        org = request.organization
        report = SLAComplianceReport.for_organization(org)
        serializer = SLAComplianceSerializer(report)
        return Response(serializer.data)
