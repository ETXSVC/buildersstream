"""Service & Warranty Management Celery tasks."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="service.check_expiring_warranties")
def check_expiring_warranties():
    """
    Daily task: expire warranties past their end_date and log warnings for
    warranties expiring within 30 days.
    """
    from .models import Warranty
    from .services import WarrantyService

    # Expire overdue active warranties
    expired_count = WarrantyService.expire_old_warranties()

    # Warn about warranties expiring within 30 days (all orgs)
    from apps.tenants.models import Organization

    warning_count = 0
    for org in Organization.objects.filter(subscription_status__in=["active", "trialing"]):
        expiring = WarrantyService.get_expiring_soon(org, days_ahead=30)
        count = expiring.count()
        if count:
            logger.warning(
                "Org %s has %d warranties expiring within 30 days", org.slug, count
            )
            warning_count += count

    logger.info(
        "check_expiring_warranties: expired=%d, expiring_soon=%d",
        expired_count, warning_count,
    )


@shared_task(name="service.expire_old_agreements")
def expire_old_agreements():
    """
    Daily task: mark service agreements past their end_date as EXPIRED.
    """
    from .services import ServiceAgreementService

    count = ServiceAgreementService.expire_old_agreements()
    logger.info("expire_old_agreements: %d agreements expired", count)


@shared_task(name="service.generate_recurring_invoices")
def generate_recurring_invoices():
    """
    Monthly task (1st of month): generate invoices for all active service agreements.
    """
    from apps.tenants.models import Organization
    from .services import ServiceAgreementService

    total = 0
    for org in Organization.objects.filter(subscription_status__in=["active", "trialing"]):
        invoices = ServiceAgreementService.generate_recurring_invoices(org)
        total += len(invoices)
        if invoices:
            logger.info("Org %s: %d recurring invoices generated", org.slug, len(invoices))

    logger.info("generate_recurring_invoices: %d total invoices created", total)
