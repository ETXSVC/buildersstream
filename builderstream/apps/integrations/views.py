"""Integration Ecosystem & Open API views."""
import logging

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationAdmin, IsOrganizationMember, IsOrganizationOwner

from .models import APIKey, IntegrationConnection, SyncLog, WebhookEndpoint
from .serializers import (
    APIKeyCreateSerializer,
    APIKeyDetailSerializer,
    APIKeyListSerializer,
    IntegrationConnectionDetailSerializer,
    IntegrationConnectionListSerializer,
    SyncLogSerializer,
    WebhookEndpointSerializer,
)
from .services import QuickBooksSyncService, WeatherService

logger = logging.getLogger(__name__)


class IntegrationConnectionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """List available integrations, connect/disconnect, and trigger syncs."""

    queryset = IntegrationConnection.objects.all()
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["integration_type", "status"]
    ordering = ["integration_type"]

    def get_serializer_class(self):
        if self.action == "list":
            return IntegrationConnectionListSerializer
        return IntegrationConnectionDetailSerializer

    @action(detail=True, methods=["post"])
    def connect(self, request, pk=None):
        """Initiate OAuth connection — returns authorization URL for OAuth flows."""
        connection = self.get_object()
        org_id = str(connection.organization_id)

        if connection.integration_type == IntegrationConnection.IntegrationType.QUICKBOOKS_ONLINE:
            auth_url = QuickBooksSyncService.get_authorization_url(org_id)
            return Response({"authorization_url": auth_url})

        return Response(
            {"detail": "OAuth not configured for this integration type."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post"])
    def disconnect(self, request, pk=None):
        """Disconnect and clear tokens for an integration."""
        connection = self.get_object()
        connection.access_token_encrypted = ""
        connection.refresh_token_encrypted = ""
        connection.token_expires_at = None
        connection.status = IntegrationConnection.Status.DISCONNECTED
        connection.save(update_fields=[
            "access_token_encrypted", "refresh_token_encrypted",
            "token_expires_at", "status", "updated_at",
        ])
        return Response({"detail": "Integration disconnected."})

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        """Trigger a manual sync for a connection (async via Celery)."""
        from .tasks import sync_quickbooks

        connection = self.get_object()
        if not connection.is_connected:
            return Response(
                {"detail": "Integration is not connected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sync_quickbooks.delay(str(connection.organization_id))
        return Response({"detail": "Sync queued."})

    @action(detail=True, methods=["get"])
    def sync_logs(self, request, pk=None):
        """List recent sync logs for a connection."""
        connection = self.get_object()
        logs = SyncLog.objects.filter(connection=connection).order_by("-started_at")[:50]
        return Response(SyncLogSerializer(logs, many=True).data)

    @action(detail=False, methods=["get"])
    def available(self, request):
        """List all integration types and their connection status for the org."""
        org_id = self.get_organization()
        connections = {
            c.integration_type: c
            for c in IntegrationConnection.objects.filter(organization_id=org_id)
        }
        result = []
        for itype, label in IntegrationConnection.IntegrationType.choices:
            conn = connections.get(itype)
            result.append({
                "integration_type": itype,
                "label": label,
                "status": conn.status if conn else "not_configured",
                "connection_id": str(conn.pk) if conn else None,
                "last_sync_at": conn.last_sync_at if conn else None,
            })
        return Response(result)


class QuickBooksOAuthView(APIView):
    """Handle QuickBooks OAuth2 callback."""

    permission_classes = [IsOrganizationAdmin]

    def get(self, request):
        """Receive OAuth2 callback with code and realmId."""
        code = request.query_params.get("code")
        realm_id = request.query_params.get("realmId")
        state = request.query_params.get("state", "")

        if not code or not realm_id:
            return Response(
                {"detail": "Missing code or realmId."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract org_id from state
        org_id = state.replace("org_", "") if state.startswith("org_") else None
        if not org_id:
            return Response({"detail": "Invalid state parameter."}, status=status.HTTP_400_BAD_REQUEST)

        redirect_uri = getattr(request, "build_absolute_uri", lambda x: x)(
            "/api/v1/integrations/quickbooks/callback/"
        )

        try:
            tokens = QuickBooksSyncService.exchange_code_for_tokens(code, redirect_uri)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import timedelta
        from django.utils import timezone

        connection, _ = IntegrationConnection.objects.get_or_create(
            organization_id=org_id,
            integration_type=IntegrationConnection.IntegrationType.QUICKBOOKS_ONLINE,
        )
        connection.access_token_encrypted = tokens["access_token"]
        connection.refresh_token_encrypted = tokens.get("refresh_token", "")
        connection.token_expires_at = timezone.now() + timedelta(seconds=tokens.get("expires_in", 3600))
        connection.status = IntegrationConnection.Status.CONNECTED
        connection.sync_config["company_id"] = realm_id
        connection.connected_by = request.user
        connection.save()

        return Response({"detail": "QuickBooks connected successfully.", "company_id": realm_id})


class WebhookEndpointViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for outbound webhook registrations (Enterprise plan only)."""

    queryset = WebhookEndpoint.objects.all()
    serializer_class = WebhookEndpointSerializer
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["is_active"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        """Send a test payload to the webhook endpoint."""
        from .services import WebhookDispatchService

        endpoint = self.get_object()
        try:
            WebhookDispatchService._send(endpoint, "test.ping", {"message": "Test webhook from BuilderStream"})
            return Response({"detail": "Test payload sent."})
        except Exception as exc:
            return Response({"detail": f"Failed: {exc}"}, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=True, methods=["post"])
    def rotate_secret(self, request, pk=None):
        """Regenerate the HMAC signing secret for this endpoint."""
        endpoint = self.get_object()
        endpoint.generate_secret()
        endpoint.save(update_fields=["secret", "updated_at"])
        return Response({"secret": endpoint.secret})


class APIKeyViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Create, list, and revoke API keys."""

    queryset = APIKey.objects.all()
    permission_classes = [IsOrganizationAdmin]
    filterset_fields = ["is_active"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return APIKeyCreateSerializer
        if self.action in ("retrieve", "partial_update", "update"):
            return APIKeyDetailSerializer
        return APIKeyListSerializer

    def perform_create(self, serializer):
        org_id = self.get_organization()
        serializer.save(organization_id=org_id, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        """Deactivate an API key."""
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save(update_fields=["is_active", "updated_at"])
        return Response({"detail": "API key revoked."})


# ---------------------------------------------------------------------------
# Public API views — authenticated via APIKey, not JWT
# ---------------------------------------------------------------------------

class PublicAPIProjectListView(APIView):
    """Public API: list projects for the authenticated API key's organization."""

    authentication_classes = []  # Uses APIKeyAuthBackend from DEFAULT settings
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.integrations.services import APIKeyAuthBackend

        auth = APIKeyAuthBackend()
        result = auth.authenticate(request)
        if result is None:
            return Response({"detail": "Invalid or missing API key."}, status=status.HTTP_401_UNAUTHORIZED)

        user, api_key = result
        if not api_key.has_scope("read:projects"):
            return Response({"detail": "Missing scope: read:projects."}, status=status.HTTP_403_FORBIDDEN)

        from apps.projects.models import Project
        from apps.projects.serializers import ProjectListSerializer

        projects = Project.objects.filter(organization=api_key.organization).order_by("-created_at")[:100]
        return Response({"results": ProjectListSerializer(projects, many=True).data})


class PublicAPIContactListView(APIView):
    """Public API: list contacts for the authenticated API key's organization."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.integrations.services import APIKeyAuthBackend

        auth = APIKeyAuthBackend()
        result = auth.authenticate(request)
        if result is None:
            return Response({"detail": "Invalid or missing API key."}, status=status.HTTP_401_UNAUTHORIZED)

        user, api_key = result
        if not api_key.has_scope("read:contacts"):
            return Response({"detail": "Missing scope: read:contacts."}, status=status.HTTP_403_FORBIDDEN)

        from apps.crm.models import Contact
        from apps.crm.serializers import ContactListSerializer

        contacts = Contact.objects.filter(organization=api_key.organization).order_by("-created_at")[:100]
        return Response({"results": ContactListSerializer(contacts, many=True).data})


class WeatherForecastView(APIView):
    """Return weather forecast for a lat/lon coordinate."""

    permission_classes = [IsOrganizationMember]

    def get(self, request):
        try:
            lat = float(request.query_params.get("lat", 0))
            lon = float(request.query_params.get("lon", 0))
        except (TypeError, ValueError):
            return Response({"detail": "Invalid lat/lon."}, status=status.HTTP_400_BAD_REQUEST)

        forecast = WeatherService.get_forecast(lat, lon)
        if forecast is None:
            return Response(
                {"detail": "Weather data unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        alerts = WeatherService.check_work_impact(forecast)
        return Response({"forecast": forecast, "work_impact_alerts": alerts})
