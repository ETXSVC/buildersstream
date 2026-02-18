"""Financial signals — activity logging and totals recalculation."""
import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# ── Cache old status for change detection ──────────────────────────────────

@receiver(pre_save, sender="financials.Invoice")
def cache_invoice_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(pre_save, sender="financials.ChangeOrder")
def cache_co_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


# ── Recalculate invoice totals when line items change ──────────────────────

@receiver(post_save, sender="financials.InvoiceLineItem")
@receiver(post_delete, sender="financials.InvoiceLineItem")
def recalculate_invoice_on_line_change(sender, instance, **kwargs):
    from .services import InvoicingService
    try:
        InvoicingService.recalculate_invoice(instance.invoice)
    except Exception:
        logger.exception("Failed to recalculate invoice totals for %s", instance.invoice_id)


# ── Recalculate CO cost_impact when line items change ─────────────────────

@receiver(post_save, sender="financials.ChangeOrderLineItem")
@receiver(post_delete, sender="financials.ChangeOrderLineItem")
def recalculate_co_on_line_change(sender, instance, **kwargs):
    from .services import ChangeOrderService
    try:
        ChangeOrderService.recalculate_cost_impact(instance.change_order)
    except Exception:
        logger.exception("Failed to recalculate CO cost impact for %s", instance.change_order_id)


# ── Recalculate PO totals when line items change ───────────────────────────

@receiver(post_save, sender="financials.PurchaseOrderLineItem")
@receiver(post_delete, sender="financials.PurchaseOrderLineItem")
def recalculate_po_on_line_change(sender, instance, **kwargs):
    from .services import PurchaseOrderService
    try:
        PurchaseOrderService.recalculate_po_totals(instance.purchase_order)
    except Exception:
        logger.exception("Failed to recalculate PO totals for %s", instance.purchase_order_id)


# ── Log activity on Invoice status change ─────────────────────────────────

@receiver(post_save, sender="financials.Invoice")
def log_invoice_status_change(sender, instance, created, **kwargs):
    if created:
        logger.info("Invoice %s created for project %s", instance.invoice_number, instance.project_id)
        return

    old_status = getattr(instance, "_old_status", None)
    if old_status and old_status != instance.status:
        logger.info(
            "Invoice %s status changed %s → %s",
            instance.invoice_number, old_status, instance.status,
        )


# ── Log activity on ChangeOrder status change ──────────────────────────────

@receiver(post_save, sender="financials.ChangeOrder")
def log_co_status_change(sender, instance, created, **kwargs):
    if created:
        logger.info("ChangeOrder #%s created for project %s", instance.number, instance.project_id)
        return

    old_status = getattr(instance, "_old_status", None)
    if old_status and old_status != instance.status:
        logger.info(
            "ChangeOrder #%s status changed %s → %s",
            instance.number, old_status, instance.status,
        )
