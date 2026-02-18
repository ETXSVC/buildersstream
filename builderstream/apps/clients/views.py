"""
Client Collaboration Portal views.

Two sets:
  Contractor-facing  (standard JWT auth, /api/v1/clients/)
    - ClientPortalAccessViewSet
    - SelectionViewSet          (+ SelectionOptionViewSet)
    - ClientApprovalViewSet
    - ClientMessageViewSet
    - PortalBrandingViewSet
    - ClientSatisfactionSurveyViewSet

  Client-facing  (Portal JWT auth, /api/v1/portal/)
    - ClientLoginView           AllowAny — trade magic link for JWT
    - ClientDashboardView       project overview + pending actions
    - ClientSelectionsView      view/choose selections
    - ClientApprovalsView       view/respond to approvals
    - ClientMessagesView        view/send messages
    - ClientScheduleView        simplified schedule
    - ClientSurveyView          submit satisfaction survey
"""

import logging

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.authentication import ClientPortalAuthentication
from apps.clients.models import (
    ClientApproval,
    ClientMessage,
    ClientPortalAccess,
    ClientSatisfactionSurvey,
    PortalBranding,
    Selection,
    SelectionOption,
)
from apps.clients.serializers import (
    ClientApprovalCreateSerializer,
    ClientApprovalDetailSerializer,
    ClientApprovalListSerializer,
    ClientMessageCreateSerializer,
    ClientMessageDetailSerializer,
    ClientMessageListSerializer,
    ClientPortalAccessCreateSerializer,
    ClientPortalAccessDetailSerializer,
    ClientPortalAccessListSerializer,
    ClientSatisfactionSurveySerializer,
    PortalApprovalResponseSerializer,
    PortalApprovalSerializer,
    PortalBrandingPublicSerializer,
    PortalBrandingSerializer,
    PortalDashboardSerializer,
    PortalMessageSendSerializer,
    PortalMessageSerializer,
    PortalProjectSerializer,
    PortalSelectionChoiceSerializer,
    PortalSelectionSerializer,
    PortalSurveySubmitSerializer,
    SelectionCreateSerializer,
    SelectionDetailSerializer,
    SelectionListSerializer,
    SelectionOptionCreateSerializer,
    SelectionOptionSerializer,
)
from apps.clients.services import (
    ApprovalService,
    ClientAuthService,
    ClientNotificationService,
    SelectionService,
)
from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember, role_required

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Contractor-facing ViewSets
# ---------------------------------------------------------------------------

class ClientPortalAccessViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """
    Manage portal access records for project clients.

    Contractors create/manage portal access; clients use magic link flow.
    """
    queryset = ClientPortalAccess.objects.select_related("contact", "project")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "contact", "is_active"]
    search_fields = ["email", "contact__first_name", "contact__last_name", "project__name"]
    ordering_fields = ["created_at", "last_login"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return ClientPortalAccessCreateSerializer
        if self.action in ("list",):
            return ClientPortalAccessListSerializer
        return ClientPortalAccessDetailSerializer

    def perform_create(self, serializer):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        instance = serializer.save(organization=org, created_by=self.request.user)
        return instance

    @action(detail=True, methods=["post"])
    def send_magic_link(self, request, pk=None):
        """
        POST /clients/portal-access/{pk}/send-magic-link/
        Send or resend the magic link email to the client.
        """
        portal_access = self.get_object()
        custom_message = request.data.get("custom_message", "")
        success = ClientAuthService.send_magic_link_email(portal_access, custom_message)
        if success:
            return Response({"detail": "Magic link email sent."})
        return Response(
            {"detail": "Failed to send magic link email. Check server logs."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """
        POST /clients/portal-access/{pk}/deactivate/
        Deactivate portal access (revoke client portal login).
        """
        portal_access = self.get_object()
        portal_access.is_active = False
        portal_access.save(update_fields=["is_active", "updated_at"])
        return Response({"detail": "Portal access deactivated."})


class SelectionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Create and manage material/finish selections for client review."""
    queryset = Selection.objects.select_related("project", "selected_option").prefetch_related("options")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "category", "assigned_to_client"]
    search_fields = ["name", "description"]
    ordering_fields = ["sort_order", "due_date", "created_at"]
    ordering = ["sort_order", "category"]

    def get_serializer_class(self):
        if self.action == "create":
            return SelectionCreateSerializer
        if self.action == "list":
            return SelectionListSerializer
        return SelectionDetailSerializer

    @action(detail=True, methods=["post"])
    def send_to_client(self, request, pk=None):
        """
        POST /clients/selections/{pk}/send-to-client/
        Move selection to CLIENT_REVIEW status.
        """
        selection = self.get_object()
        selection.status = Selection.Status.CLIENT_REVIEW
        selection.assigned_to_client = True
        selection.save(update_fields=["status", "assigned_to_client", "updated_at"])
        return Response({"detail": "Selection sent to client for review."})

    @action(detail=True, methods=["post"])
    def mark_ordered(self, request, pk=None):
        """
        POST /clients/selections/{pk}/mark-ordered/
        Advance selection to ORDERED status.
        """
        selection = self.get_object()
        if selection.status != Selection.Status.APPROVED:
            return Response(
                {"detail": "Selection must be approved before marking as ordered."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        selection.status = Selection.Status.ORDERED
        selection.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Selection marked as ordered."})


class SelectionOptionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Manage individual options within a selection."""
    queryset = SelectionOption.objects.select_related("selection")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["selection", "is_recommended"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.action == "create":
            return SelectionOptionCreateSerializer
        return SelectionOptionSerializer

    def get_queryset(self):
        # Filter by organization via selection → project → organization
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        if org:
            return self.queryset.filter(selection__organization=org)
        return self.queryset.none()


class ClientApprovalViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Create and manage formal client approval requests."""
    queryset = ClientApproval.objects.select_related("project", "contact")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "contact", "status", "approval_type"]
    search_fields = ["title", "description"]
    ordering_fields = ["requested_at", "expires_at"]
    ordering = ["-requested_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return ClientApprovalCreateSerializer
        if self.action == "list":
            return ClientApprovalListSerializer
        return ClientApprovalDetailSerializer

    def perform_create(self, serializer):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        serializer.save(organization=org, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def send_reminder(self, request, pk=None):
        """
        POST /clients/approvals/{pk}/send-reminder/
        Manually trigger a reminder email for a pending approval.
        """
        approval = self.get_object()
        success = ApprovalService.send_reminder(approval)
        if success:
            return Response({"detail": "Reminder sent."})
        return Response(
            {"detail": "Failed to send reminder. Check contact email."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ClientMessageViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Send and manage messages in client conversation threads."""
    queryset = ClientMessage.objects.select_related("project", "sender_user", "sender_contact")
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "sender_type", "is_read"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "head", "options"]  # No PATCH/DELETE on messages

    def get_serializer_class(self):
        if self.action == "create":
            return ClientMessageCreateSerializer
        if self.action == "list":
            return ClientMessageListSerializer
        return ClientMessageDetailSerializer

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """POST /clients/messages/{pk}/mark-read/"""
        message = self.get_object()
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save(update_fields=["is_read", "read_at", "updated_at"])
        return Response({"detail": "Marked as read."})


class PortalBrandingViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Manage per-organization portal branding (one record per org)."""
    queryset = PortalBranding.objects.all()
    permission_classes = [role_required(6)]  # Admin+
    serializer_class = PortalBrandingSerializer
    ordering = ["-created_at"]

    @action(detail=False, methods=["get"])
    def current(self, request):
        """
        GET /clients/branding/current/
        Return the branding config for the current organization, or 404.
        """
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        branding = PortalBranding.objects.filter(organization=org).first()
        if not branding:
            return Response({"detail": "No branding configured."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(branding)
        return Response(serializer.data)


class ClientSatisfactionSurveyViewSet(TenantViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Read satisfaction survey responses (contractor read-only)."""
    queryset = ClientSatisfactionSurvey.objects.select_related("project", "contact")
    permission_classes = [IsOrganizationMember]
    serializer_class = ClientSatisfactionSurveySerializer
    filterset_fields = ["project", "contact"]
    ordering = ["-submitted_at"]


# ---------------------------------------------------------------------------
# Client-facing portal views  (/api/v1/portal/)
# ---------------------------------------------------------------------------

class ClientLoginView(APIView):
    """
    POST /portal/login/
    AllowAny — accept magic link UUID token, validate, return scoped JWT.

    Request body:
        {
            "access_token": "<uuid-from-magic-link>",
            "pin_code": "1234"   (optional, only if portal has PIN)
        }

    Response:
        {
            "token": "<portal-jwt>",
            "project": {...},
            "contact": {...},
            "permissions": {...}
        }
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # No auth needed — this IS the auth endpoint

    def post(self, request):
        access_token = request.data.get("access_token", "").strip()
        pin_code = request.data.get("pin_code", None)

        if not access_token:
            return Response(
                {"detail": "access_token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            portal_access = ClientAuthService.validate_magic_link(access_token, pin_code)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        jwt_token = ClientAuthService.generate_portal_session_token(portal_access)
        project = portal_access.project
        contact = portal_access.contact

        return Response({
            "token": jwt_token,
            "project": {
                "id": str(project.pk),
                "name": project.name,
                "status": project.status,
            },
            "contact": {
                "id": str(contact.pk),
                "name": str(contact),
                "email": contact.email,
            },
            "permissions": portal_access.permissions,
        })


class ClientDashboardView(APIView):
    """
    GET /portal/dashboard/
    Project overview + pending counts for the authenticated client.
    """
    authentication_classes = [ClientPortalAuthentication]

    def get(self, request):
        portal_access = request.user.portal_access
        project = portal_access.project
        org = portal_access.organization

        pending_selections = Selection.objects.filter(
            organization=org,
            project=project,
            status=Selection.Status.CLIENT_REVIEW,
            assigned_to_client=True,
        ).count()

        pending_approvals = ClientApproval.objects.filter(
            organization=org,
            project=project,
            status=ClientApproval.Status.PENDING,
        ).count()

        unread_messages = ClientMessage.objects.filter(
            organization=org,
            project=project,
            sender_type=ClientMessage.SenderType.CONTRACTOR,
            is_read=False,
        ).count()

        branding = PortalBranding.objects.filter(organization=org).first()

        return Response({
            "project": {
                "id": str(project.pk),
                "name": project.name,
                "status": project.status,
                "status_display": project.get_status_display(),
                "address": getattr(project, "site_address", ""),
                "estimated_start": getattr(project, "start_date", None),
                "estimated_completion": getattr(project, "target_completion", None),
                "actual_completion": getattr(project, "actual_completion", None),
                "percent_complete": getattr(project, "percent_complete", 0),
            },
            "pending_selections": pending_selections,
            "pending_approvals": pending_approvals,
            "unread_messages": unread_messages,
            "branding": PortalBrandingPublicSerializer(branding).data if branding else None,
        })


class ClientSelectionsView(APIView):
    """
    GET  /portal/selections/           — List all selections for this project
    GET  /portal/selections/{pk}/      — Detail + options
    POST /portal/selections/{pk}/choose/ — Submit selection choice
    """
    authentication_classes = [ClientPortalAuthentication]

    def _check_selection_permission(self, request):
        if not request.user.has_permission("approve_selections"):
            return Response(
                {"detail": "You do not have permission to make selections."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def get(self, request, pk=None):
        portal_access = request.user.portal_access
        org = portal_access.organization
        project = portal_access.project

        if pk is None:
            qs = Selection.objects.filter(
                organization=org,
                project=project,
            ).exclude(status=Selection.Status.PENDING).prefetch_related("options").select_related("selected_option")
            serializer = PortalSelectionSerializer(qs, many=True)
            return Response(serializer.data)

        try:
            selection = Selection.objects.prefetch_related("options").select_related("selected_option").get(
                pk=pk, organization=org, project=project
            )
        except Selection.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PortalSelectionSerializer(selection)
        return Response(serializer.data)

    def post(self, request, pk=None):
        """POST /portal/selections/{pk}/choose/"""
        perm_error = self._check_selection_permission(request)
        if perm_error:
            return perm_error

        portal_access = request.user.portal_access
        org = portal_access.organization

        try:
            selection = Selection.objects.get(
                pk=pk, organization=org, project=portal_access.project
            )
        except Selection.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        choice_serializer = PortalSelectionChoiceSerializer(data=request.data)
        choice_serializer.is_valid(raise_exception=True)
        option_id = choice_serializer.validated_data["option_id"]

        try:
            option = SelectionOption.objects.get(pk=option_id, selection=selection)
        except SelectionOption.DoesNotExist:
            return Response({"detail": "Option not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            updated_selection = SelectionService.record_client_choice(selection, option, portal_access)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PortalSelectionSerializer(updated_selection).data)


class ClientApprovalsView(APIView):
    """
    GET  /portal/approvals/         — List pending + recent approvals
    POST /portal/approvals/{pk}/respond/ — Approve or reject
    """
    authentication_classes = [ClientPortalAuthentication]

    def get(self, request, pk=None):
        portal_access = request.user.portal_access
        org = portal_access.organization
        project = portal_access.project

        if pk is None:
            qs = ClientApproval.objects.filter(
                organization=org,
                project=project,
            ).order_by("-requested_at")[:50]
            serializer = PortalApprovalSerializer(qs, many=True)
            return Response(serializer.data)

        try:
            approval = ClientApproval.objects.get(pk=pk, organization=org, project=project)
        except ClientApproval.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(PortalApprovalSerializer(approval).data)

    def post(self, request, pk=None):
        """POST /portal/approvals/{pk}/respond/"""
        portal_access = request.user.portal_access
        org = portal_access.organization

        try:
            approval = ClientApproval.objects.get(
                pk=pk, organization=org, project=portal_access.project
            )
        except ClientApproval.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        response_serializer = PortalApprovalResponseSerializer(data=request.data)
        response_serializer.is_valid(raise_exception=True)
        data = response_serializer.validated_data

        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        try:
            updated = ApprovalService.record_approval_response(
                approval=approval,
                approved=data["approved"],
                response_notes=data.get("response_notes", ""),
                signature_data=data.get("signature_data", ""),
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PortalApprovalSerializer(updated).data)


class ClientMessagesView(APIView):
    """
    GET  /portal/messages/    — Thread of contractor↔client messages
    POST /portal/messages/    — Send a message from client to contractor
    """
    authentication_classes = [ClientPortalAuthentication]

    def get(self, request):
        portal_access = request.user.portal_access
        org = portal_access.organization
        project = portal_access.project

        messages = ClientMessage.objects.filter(
            organization=org,
            project=project,
        ).order_by("-created_at")[:100]

        # Mark contractor messages as read
        unread_ids = [m.pk for m in messages if m.sender_type == ClientMessage.SenderType.CONTRACTOR and not m.is_read]
        if unread_ids:
            ClientMessage.objects.filter(pk__in=unread_ids).update(
                is_read=True, read_at=timezone.now()
            )

        serializer = PortalMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        portal_access = request.user.portal_access
        org = portal_access.organization
        project = portal_access.project

        if not portal_access.has_permission("send_messages"):
            return Response(
                {"detail": "You do not have permission to send messages."},
                status=status.HTTP_403_FORBIDDEN,
            )

        send_serializer = PortalMessageSendSerializer(data=request.data)
        send_serializer.is_valid(raise_exception=True)
        data = send_serializer.validated_data

        message = ClientMessage.objects.create(
            organization=org,
            project=project,
            sender_type=ClientMessage.SenderType.CLIENT,
            sender_contact=portal_access.contact,
            subject=data.get("subject", ""),
            body=data["body"],
        )
        return Response(PortalMessageSerializer(message).data, status=status.HTTP_201_CREATED)


class ClientScheduleView(APIView):
    """
    GET /portal/schedule/
    Simplified project schedule for client (milestones only, no internal tasks).
    """
    authentication_classes = [ClientPortalAuthentication]

    def get(self, request):
        portal_access = request.user.portal_access

        if not portal_access.has_permission("view_schedule"):
            return Response(
                {"detail": "You do not have permission to view the schedule."},
                status=status.HTTP_403_FORBIDDEN,
            )

        project = portal_access.project

        # Import milestone model from projects app
        try:
            from apps.projects.models import ProjectMilestone
            milestones = ProjectMilestone.objects.filter(
                project=project,
            ).order_by("due_date").values(
                "id", "name", "due_date", "completed_at", "is_complete"
            )
            return Response({"milestones": list(milestones)})
        except Exception:
            return Response({"milestones": []})


class ClientSurveyView(APIView):
    """
    POST /portal/survey/
    Submit a satisfaction survey response.
    """
    authentication_classes = [ClientPortalAuthentication]

    def post(self, request):
        portal_access = request.user.portal_access
        org = portal_access.organization
        project = portal_access.project
        contact = portal_access.contact

        survey_serializer = PortalSurveySubmitSerializer(data=request.data)
        survey_serializer.is_valid(raise_exception=True)
        data = survey_serializer.validated_data

        # Prevent duplicate surveys for same milestone
        milestone = data.get("milestone", "")
        if milestone:
            exists = ClientSatisfactionSurvey.objects.filter(
                organization=org,
                project=project,
                contact=contact,
                milestone=milestone,
            ).exists()
            if exists:
                return Response(
                    {"detail": "Survey for this milestone already submitted."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        survey = ClientSatisfactionSurvey.objects.create(
            organization=org,
            project=project,
            contact=contact,
            milestone=milestone,
            rating=data["rating"],
            nps_score=data.get("nps_score"),
            feedback=data.get("feedback", ""),
        )
        return Response(
            {"detail": "Survey submitted. Thank you for your feedback!", "id": str(survey.pk)},
            status=status.HTTP_201_CREATED,
        )
