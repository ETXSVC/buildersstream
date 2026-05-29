"""Celery tasks for Integration Ecosystem."""
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="integrations.sync_quickbooks")
def sync_quickbooks(organization_id):
    """Run incremental QuickBooks sync for one organization."""
    from apps.integrations.models import IntegrationConnection
    from apps.integrations.services import QuickBooksSyncService

    try:
        connection = IntegrationConnection.objects.get(
            organization_id=organization_id,
            integration_type=IntegrationConnection.IntegrationType.QUICKBOOKS_ONLINE,
            status=IntegrationConnection.Status.CONNECTED,
        )
    except IntegrationConnection.DoesNotExist:
        logger.info("No active QB connection for org %s", organization_id)
        return

    synced, failed, errors = QuickBooksSyncService.run_incremental_sync(connection)
    logger.info("QB sync for %s: %d synced, %d failed", organization_id, synced, failed)


@shared_task(name="integrations.refresh_oauth_tokens")
def refresh_oauth_tokens():
    """Refresh OAuth tokens expiring within the next hour."""
    from apps.integrations.models import IntegrationConnection
    from apps.integrations.services import QuickBooksSyncService

    expiring_soon = timezone.now() + timezone.timedelta(hours=1)
    connections = IntegrationConnection.objects.filter(
        status=IntegrationConnection.Status.CONNECTED,
        token_expires_at__lte=expiring_soon,
    ).exclude(refresh_token_encrypted="")

    refreshed = 0
    for connection in connections:
        if QuickBooksSyncService.refresh_access_token(connection):
            refreshed += 1

    logger.info("Refreshed %d OAuth tokens", refreshed)
    return refreshed


@shared_task(name="integrations.fetch_weather_forecasts")
def fetch_weather_forecasts():
    """Update weather forecasts for all active project job sites."""
    from apps.projects.models import Project
    from apps.integrations.services import WeatherService

    active_projects = Project.objects.filter(
        status__in=["production", "punch_list"],
    ).exclude(latitude=None).exclude(longitude=None)

    updated = 0
    for project in active_projects:
        forecast = WeatherService.get_forecast(
            float(project.latitude),
            float(project.longitude),
            org_id=str(project.organization_id),
        )
        if forecast:
            updated += 1

    logger.info("Updated weather forecasts for %d projects", updated)
    return updated


@shared_task(name="integrations.dispatch_webhooks")
def dispatch_webhooks(event_type, payload, organization_id):
    """Async fan-out webhook delivery to all registered endpoints."""
    from apps.integrations.services import WebhookDispatchService
    from apps.tenants.models import Organization

    try:
        org = Organization.objects.get(pk=organization_id)
    except Organization.DoesNotExist:
        logger.error("Org %s not found for webhook dispatch", organization_id)
        return 0

    count = WebhookDispatchService.dispatch(org, event_type, payload)
    logger.info("Dispatched event %s to %d endpoints for org %s", event_type, count, organization_id)
    return count
