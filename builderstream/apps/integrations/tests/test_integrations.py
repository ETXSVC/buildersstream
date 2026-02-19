"""Tests for Integration Ecosystem & Open API (Section 17)."""
import hashlib
import hmac
import json
import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.tenants.models import Organization
from apps.tenants.context import tenant_context


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="integrations_test@example.com",
        password="pass1234!",
        first_name="Integration",
        last_name="Tester",
    )


@pytest.fixture
def org(db, user):
    return Organization.objects.create(
        name="Integration Test Co",
        slug="integration-test-co",
        owner=user,
    )


@pytest.fixture
def admin_user(db, org):
    admin = User.objects.create_user(
        email="admin_integ@example.com",
        password="pass1234!",
        first_name="Admin",
        last_name="User",
    )
    from apps.tenants.models import OrganizationMembership
    OrganizationMembership.objects.filter(organization=org, user=admin).delete()
    OrganizationMembership.objects.create(
        organization=org,
        user=admin,
        role="admin",
        is_active=True,
    )
    admin.last_active_organization = org
    admin.save()
    return admin


@pytest.fixture
def client_auth(user, org):
    user.last_active_organization = org
    user.save()
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_ORGANIZATION_ID=str(org.pk))
    return client


@pytest.fixture
def connection(db, org, user):
    from apps.integrations.models import IntegrationConnection
    with tenant_context(org):
        return IntegrationConnection.objects.create(
            organization=org,
            integration_type=IntegrationConnection.IntegrationType.QUICKBOOKS_ONLINE,
            status=IntegrationConnection.Status.CONNECTED,
            access_token_encrypted="test_access_token",
            refresh_token_encrypted="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1),
            sync_config={"company_id": "123456"},
            connected_by=user,
        )


@pytest.fixture
def webhook_endpoint(db, org):
    from apps.integrations.models import WebhookEndpoint
    with tenant_context(org):
        ep = WebhookEndpoint(
            organization=org,
            url="https://example.com/webhook",
            events=["project.status_changed", "invoice.paid"],
        )
        ep.generate_secret()
        ep.save()
        return ep


@pytest.fixture
def api_key_obj(db, org, user):
    from apps.integrations.models import APIKey
    prefix, raw_key = APIKey.generate_key()
    with tenant_context(org):
        key = APIKey.objects.create(
            organization=org,
            name="Test Key",
            key_prefix=prefix,
            key_hash=APIKey.hash_key(raw_key),
            scopes=["read:projects", "read:contacts"],
            created_by=user,
        )
    key._raw_key = raw_key  # stash for test use
    return key


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestAPIKeyModel:
    def test_generate_key_format(self):
        from apps.integrations.models import APIKey
        prefix, raw_key = APIKey.generate_key()
        assert raw_key.startswith(prefix)
        assert "_" in raw_key

    def test_hash_key_deterministic(self):
        from apps.integrations.models import APIKey
        key = "bsp_abc123_secret"
        assert APIKey.hash_key(key) == APIKey.hash_key(key)
        assert len(APIKey.hash_key(key)) == 64  # SHA-256 hex

    def test_has_scope_empty_means_all(self, db, org, user):
        from apps.integrations.models import APIKey
        prefix, raw_key = APIKey.generate_key()
        with tenant_context(org):
            key = APIKey.objects.create(
                organization=org,
                name="Wide Key",
                key_prefix=prefix,
                key_hash=APIKey.hash_key(raw_key),
                scopes=[],  # empty = unrestricted
                created_by=user,
            )
        assert key.has_scope("read:projects") is True
        assert key.has_scope("write:anything") is True

    def test_has_scope_restricted(self, db, org, user):
        from apps.integrations.models import APIKey
        prefix, raw_key = APIKey.generate_key()
        with tenant_context(org):
            key = APIKey.objects.create(
                organization=org,
                name="Read-only Key",
                key_prefix=prefix,
                key_hash=APIKey.hash_key(raw_key),
                scopes=["read:projects"],
                created_by=user,
            )
        assert key.has_scope("read:projects") is True
        assert key.has_scope("write:projects") is False


class TestWebhookEndpointModel:
    def test_generate_secret(self, db, org):
        from apps.integrations.models import WebhookEndpoint
        with tenant_context(org):
            ep = WebhookEndpoint(organization=org, url="https://example.com/hook")
            ep.generate_secret()
            assert len(ep.secret) == 64

    def test_has_event_empty_means_all(self, db, org):
        from apps.integrations.models import WebhookEndpoint
        with tenant_context(org):
            ep = WebhookEndpoint(organization=org, url="https://example.com/hook", events=[])
            assert ep.has_event("anything") is True

    def test_has_event_filtered(self, webhook_endpoint):
        assert webhook_endpoint.has_event("project.status_changed") is True
        assert webhook_endpoint.has_event("unknown.event") is False


class TestIntegrationConnectionModel:
    def test_is_connected_property(self, connection):
        assert connection.is_connected is True

    def test_is_connected_false_when_disconnected(self, db, org, user):
        from apps.integrations.models import IntegrationConnection
        with tenant_context(org):
            conn = IntegrationConnection.objects.create(
                organization=org,
                integration_type=IntegrationConnection.IntegrationType.XERO,
                status=IntegrationConnection.Status.DISCONNECTED,
                connected_by=user,
            )
        assert conn.is_connected is False

    def test_unique_per_org_type(self, db, org, user, connection):
        from apps.integrations.models import IntegrationConnection
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            with tenant_context(org):
                IntegrationConnection.objects.create(
                    organization=org,
                    integration_type=IntegrationConnection.IntegrationType.QUICKBOOKS_ONLINE,
                    connected_by=user,
                )


# ---------------------------------------------------------------------------
# API Key authentication
# ---------------------------------------------------------------------------

class TestAPIKeyAuthBackend:
    def test_valid_key_authenticates(self, rf, api_key_obj, org):
        from apps.integrations.services import APIKeyAuthBackend

        request = rf.get("/api/v1/public/projects/")
        request.META["HTTP_AUTHORIZATION"] = f"ApiKey {api_key_obj._raw_key}"
        backend = APIKeyAuthBackend()
        result = backend.authenticate(request)
        assert result is not None
        user, key = result
        assert key.pk == api_key_obj.pk

    def test_invalid_key_returns_none(self, rf, db):
        from apps.integrations.services import APIKeyAuthBackend

        request = rf.get("/api/v1/public/projects/")
        request.META["HTTP_AUTHORIZATION"] = "ApiKey bsp_fake_garbage_key"
        backend = APIKeyAuthBackend()
        result = backend.authenticate(request)
        assert result is None

    def test_expired_key_returns_none(self, rf, db, org, user):
        from apps.integrations.models import APIKey
        from apps.integrations.services import APIKeyAuthBackend

        prefix, raw_key = APIKey.generate_key()
        with tenant_context(org):
            key = APIKey.objects.create(
                organization=org,
                name="Expired Key",
                key_prefix=prefix,
                key_hash=APIKey.hash_key(raw_key),
                expires_at=timezone.now() - timedelta(hours=1),
                created_by=user,
            )
        request = rf.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"ApiKey {raw_key}"
        backend = APIKeyAuthBackend()
        result = backend.authenticate(request)
        assert result is None

    def test_wrong_scheme_returns_none(self, rf):
        from apps.integrations.services import APIKeyAuthBackend

        request = rf.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer some_jwt_token"
        backend = APIKeyAuthBackend()
        result = backend.authenticate(request)
        assert result is None


# ---------------------------------------------------------------------------
# Webhook signature verification
# ---------------------------------------------------------------------------

class TestWebhookSignatureVerification:
    def test_valid_signature(self):
        from apps.integrations.services import WebhookDispatchService

        secret = "my_test_secret"
        payload = b'{"event": "test"}'
        sig = WebhookDispatchService.sign_payload(secret, payload)
        full_sig = f"sha256={sig}"
        assert WebhookDispatchService.verify_signature(secret, payload, full_sig) is True

    def test_invalid_signature(self):
        from apps.integrations.services import WebhookDispatchService

        secret = "my_test_secret"
        payload = b'{"event": "test"}'
        assert WebhookDispatchService.verify_signature(secret, payload, "sha256=bad") is False

    def test_tampered_payload(self):
        from apps.integrations.services import WebhookDispatchService

        secret = "my_test_secret"
        original = b'{"event": "test"}'
        sig = WebhookDispatchService.sign_payload(secret, original)
        tampered = b'{"event": "fake"}'
        assert WebhookDispatchService.verify_signature(secret, tampered, f"sha256={sig}") is False


# ---------------------------------------------------------------------------
# Webhook dispatch service
# ---------------------------------------------------------------------------

class TestWebhookDispatchService:
    def test_dispatch_filters_by_event(self, db, org, webhook_endpoint):
        from apps.integrations.services import WebhookDispatchService

        with patch.object(WebhookDispatchService, "_send") as mock_send:
            count = WebhookDispatchService.dispatch(org, "unknown.event", {"x": 1})
            # endpoint only subscribed to project.status_changed and invoice.paid
            assert count == 0
            mock_send.assert_not_called()

    def test_dispatch_calls_matching_endpoint(self, db, org, webhook_endpoint):
        from apps.integrations.services import WebhookDispatchService

        with patch.object(WebhookDispatchService, "_send") as mock_send:
            count = WebhookDispatchService.dispatch(org, "invoice.paid", {"amount": 100})
            assert count == 1
            mock_send.assert_called_once()

    def test_dispatch_handles_send_failure_gracefully(self, db, org, webhook_endpoint):
        from apps.integrations.services import WebhookDispatchService

        with patch.object(WebhookDispatchService, "_send", side_effect=Exception("connection error")):
            # Should not raise — errors are caught and logged
            count = WebhookDispatchService.dispatch(org, "invoice.paid", {"amount": 100})
            assert count == 0


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

class TestIntegrationConnectionAPI:
    def test_list_connections(self, client_auth, org, connection):
        with tenant_context(org):
            url = "/api/v1/integrations/connections/"
        resp = client_auth.get("/api/v1/integrations/connections/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 1

    def test_available_integrations(self, client_auth, org):
        resp = client_auth.get("/api/v1/integrations/connections/available/")
        assert resp.status_code == 200
        types = [item["integration_type"] for item in resp.json()]
        assert "quickbooks_online" in types

    def test_disconnect(self, client_auth, connection):
        resp = client_auth.post(f"/api/v1/integrations/connections/{connection.pk}/disconnect/")
        assert resp.status_code == 200
        connection.refresh_from_db()
        assert connection.status == "disconnected"

    def test_sync_requires_connected_status(self, db, org, user, client_auth):
        from apps.integrations.models import IntegrationConnection
        with tenant_context(org):
            conn = IntegrationConnection.objects.create(
                organization=org,
                integration_type=IntegrationConnection.IntegrationType.XERO,
                status=IntegrationConnection.Status.DISCONNECTED,
                connected_by=user,
            )
        resp = client_auth.post(f"/api/v1/integrations/connections/{conn.pk}/sync/")
        assert resp.status_code == 400


class TestAPIKeyAPI:
    def test_create_api_key_returns_raw_key_once(self, client_auth, org):
        resp = client_auth.post("/api/v1/integrations/api-keys/", {
            "name": "My Test Key",
            "scopes": ["read:projects"],
            "rate_limit_per_hour": 500,
        }, format="json")
        assert resp.status_code == 201
        data = resp.json()
        assert "raw_key" in data
        assert data["raw_key"].startswith("bsp_")

    def test_list_keys_does_not_expose_raw_key(self, client_auth, api_key_obj):
        resp = client_auth.get("/api/v1/integrations/api-keys/")
        assert resp.status_code == 200
        for key in resp.json()["results"]:
            assert "raw_key" not in key
            assert "key_hash" not in key

    def test_revoke_key(self, client_auth, api_key_obj):
        resp = client_auth.post(f"/api/v1/integrations/api-keys/{api_key_obj.pk}/revoke/")
        assert resp.status_code == 200
        api_key_obj.refresh_from_db()
        assert api_key_obj.is_active is False


class TestWebhookEndpointAPI:
    def test_create_webhook_auto_generates_secret(self, client_auth):
        resp = client_auth.post("/api/v1/integrations/webhooks/", {
            "url": "https://myapp.com/hooks/builderstream",
            "events": ["project.status_changed"],
        }, format="json")
        assert resp.status_code == 201
        # Secret should not appear in response
        assert "secret" not in resp.json()

    def test_rotate_secret(self, client_auth, webhook_endpoint):
        old_secret = webhook_endpoint.secret
        resp = client_auth.post(f"/api/v1/integrations/webhooks/{webhook_endpoint.pk}/rotate_secret/")
        assert resp.status_code == 200
        assert "secret" in resp.json()
        webhook_endpoint.refresh_from_db()
        assert webhook_endpoint.secret != old_secret


# ---------------------------------------------------------------------------
# Weather service tests
# ---------------------------------------------------------------------------

class TestWeatherService:
    def test_get_forecast_returns_none_without_api_key(self, settings):
        from apps.integrations.services import WeatherService

        settings.OPENWEATHERMAP_API_KEY = ""
        result = WeatherService.get_forecast(40.7128, -74.0060)
        assert result is None

    def test_check_work_impact_high_wind(self):
        from apps.integrations.services import WeatherService

        forecast = {
            "forecasts": [
                {"dt": 1700000000, "temp": 72, "wind_speed": 30, "precipitation": 0},
            ]
        }
        alerts = WeatherService.check_work_impact(forecast)
        types = [a["type"] for a in alerts]
        assert "high_wind" in types

    def test_check_work_impact_freezing(self):
        from apps.integrations.services import WeatherService

        forecast = {
            "forecasts": [
                {"dt": 1700000000, "temp": 20, "wind_speed": 5, "precipitation": 0},
            ]
        }
        alerts = WeatherService.check_work_impact(forecast)
        types = [a["type"] for a in alerts]
        assert "freezing" in types

    def test_check_work_impact_no_alerts_normal(self):
        from apps.integrations.services import WeatherService

        forecast = {
            "forecasts": [
                {"dt": 1700000000, "temp": 72, "wind_speed": 10, "precipitation": 0.1},
            ]
        }
        alerts = WeatherService.check_work_impact(forecast)
        assert alerts == []

    def test_check_work_impact_empty_forecast(self):
        from apps.integrations.services import WeatherService

        assert WeatherService.check_work_impact(None) == []
        assert WeatherService.check_work_impact({}) == []


# ---------------------------------------------------------------------------
# QuickBooks OAuth tests
# ---------------------------------------------------------------------------

class TestQuickBooksOAuth:
    def test_get_authorization_url(self, settings):
        from apps.integrations.services import QuickBooksSyncService

        settings.QUICKBOOKS_CLIENT_ID = "test_client_id"
        settings.QUICKBOOKS_REDIRECT_URI = "http://localhost/callback"
        url = QuickBooksSyncService.get_authorization_url("org_123")
        assert "client_id=test_client_id" in url
        assert "state=org_org_123" in url
        assert "quickbooks" in url.lower() or "intuit" in url.lower()

    def test_exchange_code_raises_on_http_error(self, settings):
        from apps.integrations.services import QuickBooksSyncService
        import requests as req_lib

        settings.QUICKBOOKS_CLIENT_ID = "test_id"
        settings.QUICKBOOKS_CLIENT_SECRET = "test_secret"

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = req_lib.RequestException("401 Unauthorized")
            mock_post.return_value = mock_resp
            with pytest.raises(ValueError, match="Token exchange failed"):
                QuickBooksSyncService.exchange_code_for_tokens("bad_code", "http://localhost/cb")

    def test_refresh_access_token_updates_connection(self, db, org, user, connection):
        from apps.integrations.services import QuickBooksSyncService

        new_token_data = {
            "access_token": "new_access_token_xyz",
            "refresh_token": "new_refresh_token_xyz",
            "expires_in": 3600,
        }
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = new_token_data
            mock_post.return_value = mock_resp

            result = QuickBooksSyncService.refresh_access_token(connection)

        assert result is True
        connection.refresh_from_db()
        assert connection.access_token_encrypted == "new_access_token_xyz"
        assert connection.status == "connected"
