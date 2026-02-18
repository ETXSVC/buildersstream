"""Field Operations Hub Celery tasks."""
import logging
from datetime import date, timedelta

from celery import shared_task
from django.utils import timezone as django_tz

logger = logging.getLogger(__name__)


@shared_task(name="field_ops.auto_clock_out")
def auto_clock_out():
    """Nightly: auto clock-out time entries open for more than 14 hours.

    Flags them with a note for supervisor review.
    """
    from .models import TimeEntry
    from .services import TimeClockService

    threshold = django_tz.now() - timedelta(hours=14)
    open_entries = TimeEntry.objects.filter(
        clock_in__lte=threshold,
        clock_out__isnull=True,
        entry_type=TimeEntry.EntryType.CLOCK,
    ).select_related("user", "project")

    count = 0
    for entry in open_entries:
        try:
            entry.notes = (
                f"[AUTO CLOCK-OUT] Entry open >14h, automatically clocked out at "
                f"{django_tz.now().strftime('%Y-%m-%d %H:%M')}. Please review."
                + (" " + entry.notes if entry.notes else "")
            )
            TimeClockService.clock_out(entry)
            count += 1
            logger.warning(
                "Auto clocked out user %s on project %s (entry %s)",
                entry.user_id, entry.project_id, entry.pk,
            )
        except Exception:
            logger.exception("Failed to auto clock-out entry %s", entry.pk)

    logger.info("auto_clock_out: processed %d entries", count)
    return count


@shared_task(name="field_ops.reminder_daily_log")
def reminder_daily_log():
    """Daily at 4pm: remind project managers/supers of projects without daily logs today."""
    from django.conf import settings
    from django.core.mail import send_mail

    from apps.projects.models import Project
    from apps.tenants.models import Membership

    from .models import DailyLog

    today = django_tz.localdate()

    # Find active projects that don't have a daily log for today
    projects_with_log = DailyLog.objects.filter(log_date=today).values_list("project_id", flat=True)
    active_projects = Project.objects.filter(
        status__in=["production", "punch_list"]
    ).exclude(id__in=projects_with_log).select_related("organization")

    reminded = 0
    for project in active_projects:
        # Find the PM or OWNER for this project
        pm_memberships = Membership.objects.filter(
            organization=project.organization,
            role__in=["owner", "admin", "pm"],
        ).select_related("user")

        for membership in pm_memberships[:1]:  # email first PM/admin/owner
            try:
                send_mail(
                    subject=f"BuilderStream — Daily log missing for {project.name}",
                    message=(
                        f"Hi {membership.user.first_name},\n\n"
                        f"No daily log has been submitted today ({today}) for:\n\n"
                        f"  Project: {project.name} ({project.project_number})\n\n"
                        "Please submit a daily log before end of day.\n\n"
                        "The BuilderStream Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[membership.user.email],
                    fail_silently=True,
                )
                reminded += 1
            except Exception:
                logger.exception("Failed to send daily log reminder for project %s", project.pk)

    logger.info("reminder_daily_log: sent %d reminders for %d projects", reminded, active_projects.count())
    return reminded


@shared_task(name="field_ops.calculate_overtime")
def calculate_overtime():
    """Nightly: recalculate weekly overtime totals for all pending time entries."""
    from django.contrib.auth import get_user_model

    from apps.tenants.models import Organization

    from .services import TimeClockService

    User = get_user_model()

    # Get start of current week (Monday)
    today = django_tz.localdate()
    week_start = today - timedelta(days=today.weekday())

    updated_total = 0
    for org in Organization.objects.filter(subscription_status__in=["active", "trialing"]):
        # Get all users with entries this week in this org
        from .models import TimeEntry

        user_ids = (
            TimeEntry.objects.filter(
                organization=org,
                date__gte=week_start,
                status=TimeEntry.Status.PENDING,
            )
            .values_list("user_id", flat=True)
            .distinct()
        )

        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                updated = TimeClockService.calculate_weekly_overtime(user, org, week_start)
                updated_total += len(updated)
            except Exception:
                logger.exception(
                    "Failed to calculate overtime for user %s in org %s", user_id, org.pk
                )

    logger.info("calculate_overtime: updated %d time entries", updated_total)
    return updated_total
