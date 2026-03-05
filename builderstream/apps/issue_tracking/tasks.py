"""Issue Tracking Celery tasks."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="issue_tracking.check_sla_breaches")
def check_sla_breaches():
    """Check and mark SLA breaches every 15 minutes."""
    from .services import SLAService

    try:
        SLAService.check_sla_breaches()
    except Exception:
        logger.exception("SLA breach check failed")


@shared_task(name="issue_tracking.send_sla_warning_notifications")
def send_sla_warning_notifications():
    """Warn assignees when SLA deadline is approaching (within 30 min)."""
    from datetime import timedelta

    from django.utils import timezone

    from .models import Issue

    now = timezone.now()
    warning_window = now + timedelta(minutes=30)
    open_statuses = [
        Issue.Status.NEW,
        Issue.Status.OPEN,
        Issue.Status.IN_PROGRESS,
        Issue.Status.PENDING,
    ]

    approaching = Issue.objects.unscoped().filter(
        status__in=open_statuses,
        sla_resolution_due_at__lte=warning_window,
        sla_resolution_due_at__gt=now,
        sla_resolution_met__isnull=True,
    ).select_related("assignee", "issue_type")

    for issue in approaching:
        if issue.assignee:
            logger.info(
                "SLA warning: issue %s due at %s, assigned to %s",
                issue.number,
                issue.sla_resolution_due_at,
                issue.assignee.email,
            )
            # Full notification dispatch would call NotificationService here
