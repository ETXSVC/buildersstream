"""Service & Warranty Management signals."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

_ticket_status_cache = {}
_claim_status_cache = {}


@receiver(pre_save, sender="service.ServiceTicket")
def cache_ticket_status(sender, instance, **kwargs):
    """Cache previous ticket status for change detection."""
    if instance.pk:
        _ticket_status_cache[instance.pk] = instance.status


@receiver(post_save, sender="service.ServiceTicket")
def on_ticket_saved(sender, instance, created, **kwargs):
    """Log ticket creation and status transitions."""
    if created:
        logger.info(
            "ServiceTicket %s (%s) created in org %s",
            instance.ticket_number, instance.title, instance.organization_id,
        )
        return

    old_status = _ticket_status_cache.pop(instance.pk, None)
    if old_status and old_status != instance.status:
        logger.info(
            "ServiceTicket %s status changed: %s → %s",
            instance.ticket_number, old_status, instance.status,
        )


@receiver(pre_save, sender="service.WarrantyClaim")
def cache_claim_status(sender, instance, **kwargs):
    """Cache previous claim status for change detection."""
    if instance.pk:
        _claim_status_cache[instance.pk] = instance.status


@receiver(post_save, sender="service.WarrantyClaim")
def on_claim_saved(sender, instance, created, **kwargs):
    """Log warranty claim creation and status transitions."""
    if created:
        logger.info(
            "WarrantyClaim %s filed on warranty %s", instance.pk, instance.warranty_id
        )
        return

    old_status = _claim_status_cache.pop(instance.pk, None)
    if old_status and old_status != instance.status:
        logger.info(
            "WarrantyClaim %s status changed: %s → %s",
            instance.pk, old_status, instance.status,
        )
