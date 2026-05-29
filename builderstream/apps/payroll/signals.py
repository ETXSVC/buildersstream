"""Payroll signals — activity logging for payroll run status changes."""
import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender="payroll.PayrollRun")
def cache_payroll_run_status(sender, instance, **kwargs):
    """Cache previous status on the instance for change detection."""
    if instance.pk:
        instance._old_status = instance.status


@receiver(post_save, sender="payroll.PayrollRun")
def on_payroll_run_saved(sender, instance, created, **kwargs):
    """Log status transitions on payroll runs."""
    if created:
        logger.info(
            "PayrollRun %s created for org %s (period %s – %s)",
            instance.pk, instance.organization_id,
            instance.pay_period_start, instance.pay_period_end,
        )
        return

    old_status = getattr(instance, "_old_status", None)
    if old_status and old_status != instance.status:
        logger.info(
            "PayrollRun %s status changed: %s → %s",
            instance.pk, old_status, instance.status,
        )
