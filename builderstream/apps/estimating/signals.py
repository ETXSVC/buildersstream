"""
Signal handlers for the estimating app.

Signals:
- post_save/post_delete on EstimateLineItem -> recalculate estimate totals
- post_save/post_delete on AssemblyItem -> recalculate assembly totals
- pre_save on CostItem -> auto-calculate markup percentage
- pre_save on Proposal -> cache old status for change detection
- post_save on Proposal -> log activity when status changes
"""

import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CostItem: auto-calculate markup_percent before save
# ---------------------------------------------------------------------------

@receiver(pre_save, sender='estimating.CostItem')
def calculate_cost_item_markup(sender, instance, **kwargs):
    """Auto-calculate markup_percent from cost and base_price when either changes."""
    if instance.cost and instance.cost > 0 and instance.base_price:
        markup = ((instance.base_price - instance.cost) / instance.cost) * 100
        instance.markup_percent = round(markup, 2)


# ---------------------------------------------------------------------------
# AssemblyItem: recalculate parent Assembly totals
# ---------------------------------------------------------------------------

@receiver(post_save, sender='estimating.AssemblyItem')
def recalculate_assembly_on_item_save(sender, instance, **kwargs):
    """Recalculate assembly totals whenever an assembly item is saved."""
    try:
        from apps.estimating.services import EstimateCalculationService
        EstimateCalculationService.calculate_assembly_totals(instance.assembly)
    except Exception as exc:
        logger.exception(
            "Failed to recalculate assembly %s totals after AssemblyItem save: %s",
            instance.assembly_id,
            exc,
        )


@receiver(post_delete, sender='estimating.AssemblyItem')
def recalculate_assembly_on_item_delete(sender, instance, **kwargs):
    """Recalculate assembly totals whenever an assembly item is deleted."""
    try:
        from apps.estimating.services import EstimateCalculationService
        instance.assembly.refresh_from_db()
        EstimateCalculationService.calculate_assembly_totals(instance.assembly)
    except Exception as exc:
        logger.exception(
            "Failed to recalculate assembly %s totals after AssemblyItem delete: %s",
            instance.assembly_id,
            exc,
        )


# ---------------------------------------------------------------------------
# EstimateLineItem: recalculate parent Estimate section + total
# ---------------------------------------------------------------------------

@receiver(post_save, sender='estimating.EstimateLineItem')
def recalculate_estimate_on_line_item_save(sender, instance, created, **kwargs):
    """Recalculate estimate totals whenever a line item is saved."""
    try:
        from apps.estimating.services import EstimateCalculationService
        estimate = instance.section.estimate
        EstimateCalculationService.calculate_estimate_totals(estimate)
    except Exception as exc:
        logger.exception(
            "Failed to recalculate estimate totals after EstimateLineItem save: %s",
            exc,
        )


@receiver(post_delete, sender='estimating.EstimateLineItem')
def recalculate_estimate_on_line_item_delete(sender, instance, **kwargs):
    """Recalculate estimate totals whenever a line item is deleted."""
    try:
        from apps.estimating.services import EstimateCalculationService
        estimate = instance.section.estimate
        estimate.refresh_from_db()
        EstimateCalculationService.calculate_estimate_totals(estimate)
    except Exception as exc:
        logger.exception(
            "Failed to recalculate estimate totals after EstimateLineItem delete: %s",
            exc,
        )


# ---------------------------------------------------------------------------
# Proposal: status change tracking and activity logging
# ---------------------------------------------------------------------------

@receiver(pre_save, sender='estimating.Proposal')
def cache_proposal_old_status(sender, instance, **kwargs):
    """Cache previous status on instance so post_save can detect changes."""
    if instance.pk:
        try:
            from apps.estimating.models import Proposal
            old = Proposal.objects.filter(pk=instance.pk).values('status').first()
            instance._old_status = old['status'] if old else None
        except Exception:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender='estimating.Proposal')
def log_proposal_status_change(sender, instance, created, **kwargs):
    """Log activity when a proposal status changes."""
    if created:
        logger.info(
            "Proposal %s created (number: %s) for estimate %s",
            instance.pk,
            instance.proposal_number,
            instance.estimate_id,
        )
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status and old_status != instance.status:
        logger.info(
            "Proposal %s status changed: %s -> %s",
            instance.pk,
            old_status,
            instance.status,
        )
        # Queue signed notification for the estimate's assigned user
        if instance.status == 'signed' and instance.estimate.assigned_to_id:
            try:
                from apps.estimating.tasks import notify_proposal_signed
                notify_proposal_signed.delay(str(instance.pk))
            except Exception as exc:
                logger.warning(
                    "Could not queue proposal-signed notification for %s: %s",
                    instance.pk,
                    exc,
                )
