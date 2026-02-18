"""Quality & Safety Celery tasks."""
import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="quality_safety.check_overdue_inspections")
def check_overdue_inspections():
    """Flag scheduled inspections whose inspection_date has passed."""
    from .models import Inspection

    today = date.today()
    overdue = Inspection.objects.filter(
        status=Inspection.Status.SCHEDULED,
        inspection_date__lt=today,
    )
    count = overdue.count()
    if count:
        logger.warning("Found %d overdue scheduled inspections.", count)
    return count


@shared_task(name="quality_safety.check_overdue_deficiencies")
def check_overdue_deficiencies():
    """Log deficiencies past their due date that are still open."""
    from .models import Deficiency

    today = date.today()
    overdue = Deficiency.objects.filter(
        status__in=(Deficiency.Status.OPEN, Deficiency.Status.IN_PROGRESS),
        due_date__lt=today,
    )
    count = overdue.count()
    if count:
        logger.warning("Found %d overdue open deficiencies.", count)
    return count


@shared_task(name="quality_safety.generate_weekly_safety_report")
def generate_weekly_safety_report():
    """Log a weekly safety summary per organization."""
    from apps.tenants.models import Organization

    from .services import QualityAnalyticsService

    orgs = Organization.objects.filter(subscription_status__in=["active", "trialing"])
    for org in orgs:
        try:
            summary = QualityAnalyticsService.get_safety_summary(org)
            logger.info(
                "Weekly safety report | org=%s incidents_ytd=%s osha=%s open=%s tbt=%s",
                org.slug,
                summary["incidents_ytd"],
                summary["osha_reportable_ytd"],
                summary["open_incidents"],
                summary["toolbox_talks_ytd"],
            )
        except Exception:
            logger.exception("Error generating weekly safety report for org %s", org.pk)
