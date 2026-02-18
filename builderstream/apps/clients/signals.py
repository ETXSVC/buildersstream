"""
Client Collaboration Portal signal handlers.

Signals:
  - pre_save(ClientApproval)  — cache old status for change detection
  - post_save(ClientApproval) — log activity when status changes
  - post_save(ClientMessage)  — send real-time notification when contractor sends message
"""

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender="clients.ClientApproval")
def cache_approval_old_status(sender, instance, **kwargs):
    """
    Cache the existing status before save so post_save can detect changes.
    """
    if instance.pk:
        from apps.clients.models import ClientApproval
        old = ClientApproval.objects.filter(pk=instance.pk).values("status").first()
        instance._old_status = old["status"] if old else None
    else:
        instance._old_status = None


@receiver(post_save, sender="clients.ClientApproval")
def log_approval_status_change(sender, instance, created, **kwargs):
    """
    Log an activity entry when an approval status changes.
    """
    old_status = getattr(instance, "_old_status", None)

    if created:
        _log_approval_activity(instance, "created", f"Approval request created: {instance.title}")
        return

    if old_status and old_status != instance.status:
        _log_approval_activity(
            instance,
            "updated",
            f"Approval status changed: {old_status} → {instance.status} ({instance.title})",
        )


def _log_approval_activity(approval, action, message):
    try:
        from apps.projects.models import ActivityLog
        ActivityLog.objects.create(
            organization=approval.organization,
            project=approval.project,
            user=None,
            action=action,
            description=message,
            changes={"approval_id": str(approval.pk), "status": approval.status},
        )
    except Exception as exc:
        logger.warning("Failed to log approval activity: %s", exc)


@receiver(post_save, sender="clients.ClientMessage")
def notify_realtime_client_on_contractor_message(sender, instance, created, **kwargs):
    """
    When a contractor sends a message and the client has realtime notifications,
    send an email notification immediately.
    """
    if not created:
        return

    if instance.sender_type != "CONTRACTOR":
        return

    try:
        from apps.clients.models import ClientPortalAccess

        # Find active portal accesses for this project
        accesses = ClientPortalAccess.objects.filter(
            organization=instance.organization,
            project=instance.project,
            is_active=True,
            permissions__contains={"send_messages": True},
        ).select_related("contact")

        for access in accesses:
            pref = access.permissions.get("notification_preference", "daily")
            if pref == "realtime":
                from apps.clients.services import ClientNotificationService
                ClientNotificationService._send_generic_email(
                    access,
                    subject=f"New message: {instance.subject or 'No subject'} — {instance.project.name}",
                    body=(
                        f"You have a new message from your project team.\n\n"
                        f"{instance.body[:500]}\n\n"
                        f"Log in to your portal to view and reply."
                    ),
                )
    except Exception as exc:
        logger.warning("Failed to send real-time message notification: %s", exc)
