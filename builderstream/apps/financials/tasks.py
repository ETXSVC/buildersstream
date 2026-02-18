"""Financial Management Suite — Celery tasks."""
import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="financials.check_overdue_invoices")
def check_overdue_invoices():
    """Mark unpaid past-due invoices as overdue. Runs daily."""
    from apps.tenants.models import Organization
    from .services import InvoicingService

    total_updated = 0
    for org in Organization.objects.filter(is_active=True):
        updated = InvoicingService.check_and_mark_overdue(org)
        total_updated += updated

    logger.info("check_overdue_invoices: marked %d invoices overdue", total_updated)
    return total_updated


@shared_task(name="financials.calculate_budget_variances")
def calculate_budget_variances():
    """Sync expense actuals to budget lines for all active projects. Runs hourly."""
    from apps.projects.models import Project
    from .services import JobCostingService

    projects = Project.objects.filter(
        is_active=True, is_archived=False
    ).exclude(status__in=["completed", "canceled"])

    count = 0
    for project in projects:
        try:
            JobCostingService.update_budget_actuals(project)
            count += 1
        except Exception:
            logger.exception("Failed to update budget actuals for project %s", project.pk)

    logger.info("calculate_budget_variances: synced %d projects", count)
    return count


@shared_task(name="financials.generate_aging_report")
def generate_aging_report():
    """Generate and log invoice aging summary. Runs weekly (Mondays)."""
    from .models import Invoice

    today = date.today()
    buckets = {
        "current": 0,
        "1_30_days": 0,
        "31_60_days": 0,
        "61_90_days": 0,
        "over_90_days": 0,
    }
    totals = {k: 0.0 for k in buckets}

    outstanding = Invoice.objects.filter(
        status__in=["sent", "viewed", "partial", "overdue"]
    ).values("due_date", "balance_due")

    for inv in outstanding:
        due = inv["due_date"]
        bal = float(inv["balance_due"] or 0)
        if due is None or due >= today:
            buckets["current"] += 1
            totals["current"] += bal
        else:
            days_overdue = (today - due).days
            if days_overdue <= 30:
                buckets["1_30_days"] += 1
                totals["1_30_days"] += bal
            elif days_overdue <= 60:
                buckets["31_60_days"] += 1
                totals["31_60_days"] += bal
            elif days_overdue <= 90:
                buckets["61_90_days"] += 1
                totals["61_90_days"] += bal
            else:
                buckets["over_90_days"] += 1
                totals["over_90_days"] += bal

    logger.info(
        "generate_aging_report: current=%d($%.2f) 1-30=%d($%.2f) 31-60=%d($%.2f) "
        "61-90=%d($%.2f) 90+=%d($%.2f)",
        buckets["current"], totals["current"],
        buckets["1_30_days"], totals["1_30_days"],
        buckets["31_60_days"], totals["31_60_days"],
        buckets["61_90_days"], totals["61_90_days"],
        buckets["over_90_days"], totals["over_90_days"],
    )
    return {"buckets": buckets, "totals": totals}
