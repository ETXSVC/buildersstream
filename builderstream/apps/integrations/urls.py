"""Integration Ecosystem URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIKeyViewSet,
    IntegrationConnectionViewSet,
    PublicAPIContactListView,
    PublicAPIProjectListView,
    QuickBooksOAuthView,
    WeatherForecastView,
    WebhookEndpointViewSet,
)

router = DefaultRouter()
router.register(r"connections", IntegrationConnectionViewSet, basename="connection")
router.register(r"webhooks", WebhookEndpointViewSet, basename="webhook")
router.register(r"api-keys", APIKeyViewSet, basename="api-key")

app_name = "integrations"

urlpatterns = [
    path("", include(router.urls)),
    # QuickBooks OAuth callback
    path("quickbooks/callback/", QuickBooksOAuthView.as_view(), name="quickbooks-callback"),
    # Weather
    path("weather/forecast/", WeatherForecastView.as_view(), name="weather-forecast"),
]

# Public API endpoints (API-key authenticated, not JWT)
public_api_urlpatterns = [
    path("projects/", PublicAPIProjectListView.as_view(), name="public-projects"),
    path("contacts/", PublicAPIContactListView.as_view(), name="public-contacts"),
]
