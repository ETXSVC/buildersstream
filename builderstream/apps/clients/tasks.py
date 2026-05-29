"""
Client Collaboration Portal Celery tasks.

Tasks:
  send_client_daily_digest    — Daily 8am, compile and send updates to daily-digest clients
  send_approval_reminders     — Daily, remind clients of pending approvals past threshold
  send_satisfaction_survey    — On-demand, send NPS survey after configurable delay
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_client_daily_digest(self):
    """
    Daily digest task — scheduled at 8am.

    Sends a summary email to all active portal clients with "daily" notification
    preference, covering updates from the last 24 hours:
    - New contractor messages
    - Pending approval requests
    - Pending selections awaiting choice
    """
    from apps.clients.models import ClientPortalAccess
    from apps.clients.services import ClientNotificationService

    # Only notify clients with daily preference
    accesses = ClientPortalAccess.objects.filter(
        is_active=True,
    ).select_related("contact", "project", "organization")

    sent_count = 0
    failed_count = 0

    for access in accesses:
        pref = access.permissions.get("notification_preference", "daily")
        if pref != "daily":
            continue

        try:
            digest_data = ClientNotificationService.compile_daily_digest_data(access)

            # Only send if there's something to report
            total_updates = (
                digest_data["new_messages"]
                + digest_data["pending_approvals"]
                + digest_data["pending_selections"]
            )
            if total_updates == 0:
                continue

            ClientNotificationService.send_daily_digest(access, digest_data)
            sent_count += 1
        except Exception as exc:
            failed_count += 1
            logger.error(
                "Failed to send daily digest to portal_access %s: %s",
                access.pk,
                exc,
            )

    logger.info(
        "Daily digest task complete — sent: %d, failed: %d",
        sent_count,
        failed_count,
    )
    return {"sent": sent_count, "failed": failed_count}


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_approval_reminders(self):
    """
    Daily approval reminder task.

    Sends reminder emails for pending approval requests that:
    - Have been pending for more than REMINDER_THRESHOLD_DAYS
    - Have a contact with an email address
    - Are not expired
    """
    from apps.clients.models import ClientApproval
    from apps.clients.services import ApprovalService

    # First, expire overdue approvals
    expired = ApprovalService.expire_overdue_approvals()
    if expired:
        logger.info("Expired %d overdue approvals.", expired)

    # Get approvals needing reminder
    pending_approvals = ApprovalService.get_pending_approvals_needing_reminder()

    reminded_count = 0
    failed_count = 0

    for approval in pending_approvals:
        try:
            success = ApprovalService.send_reminder(approval)
            if success:
                reminded_count += 1
            else:
                failed_count += 1
        except Exception as exc:
            failed_count += 1
            logger.error("Failed to send reminder for approval %s: %s", approval.pk, exc)

    logger.info(
        "Approval reminders task complete — reminded: %d, failed: %d, expired: %d",
        reminded_count,
        failed_count,
        expired,
    )
    return {"reminded": reminded_count, "failed": failed_count, "expired": expired}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_satisfaction_survey(self, portal_access_id: str, milestone: str):
    """
    On-demand task triggered after a project milestone is completed.

    Args:
        portal_access_id: UUID string of ClientPortalAccess record
        milestone: Milestone name that triggered the survey
    """
    from apps.clients.models import ClientPortalAccess
    from apps.clients.services import ClientNotificationService

    try:
        portal_access = ClientPortalAccess.objects.select_related(
            "contact", "project", "organization"
        ).get(pk=portal_access_id, is_active=True)
    except ClientPortalAccess.DoesNotExist:
        logger.warning("send_satisfaction_survey: portal_access %s not found.", portal_access_id)
        return False

    success = ClientNotificationService.send_satisfaction_survey(portal_access, milestone)
    if success:
        logger.info(
            "Satisfaction survey sent to %s for milestone '%s'",
            portal_access.email,
            milestone,
        )
    return success


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_portal_magic_link(self, portal_access_id: str, custom_message: str = ""):
    """
    On-demand task to send a magic link email asynchronously.

    Args:
        portal_access_id: UUID string of ClientPortalAccess record
        custom_message: Optional custom message from contractor
    """
    from apps.clients.models import ClientPortalAccess
    from apps.clients.services import ClientAuthService

    try:
        portal_access = ClientPortalAccess.objects.select_related(
            "contact", "project", "organization"
        ).get(pk=portal_access_id, is_active=True)
    except ClientPortalAccess.DoesNotExist:
        logger.warning("send_portal_magic_link: portal_access %s not found.", portal_access_id)
        return False

    success = ClientAuthService.send_magic_link_email(portal_access, custom_message or None)
    return success
