"""
NotificationService — create and deliver notifications via WebSocket + email.

Usage:
    NotificationService.notify(
        user=user,
        org=org,
        notification_type=Notification.NotificationType.RFI_SUBMITTED,
        title="New RFI submitted",
        body="John submitted RFI #4 on Project Alpha",
        data={"project_id": "...", "rfi_id": "...", "url": "/projects/.../rfis/..."},
    )
"""
import json
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    def notify(
        user,
        org,
        notification_type: str,
        title: str,
        body: str = "",
        data: dict | None = None,
        priority: str = "normal",
    ):
        """Create a Notification record and push to WebSocket group."""
        from apps.notifications.models import Notification, NotificationPreference

        data = data or {}

        # Check preferences
        prefs = NotificationService._get_prefs(user, org)
        if prefs and not prefs.in_app_enabled:
            return None

        notif = Notification.objects.create(
            org=org,
            recipient=user,
            notification_type=notification_type,
            priority=priority,
            title=title,
            body=body,
            data=data,
        )

        # Push via WebSocket (fire-and-forget, don't crash on channel layer errors)
        try:
            NotificationService.send_to_user(user, {
                "type": "notification_message",
                "id": str(notif.pk),
                "notification_type": notification_type,
                "priority": priority,
                "title": title,
                "body": body,
                "data": data,
                "created_at": notif.created_at.isoformat(),
            })
        except Exception:
            logger.exception("Failed to push WebSocket notification %s", notif.pk)

        return notif

    @staticmethod
    def send_to_user(user, payload: dict):
        """Send a message to a user's WebSocket channel group."""
        channel_layer = get_channel_layer()
        group_name = f"user_{user.pk}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "notification_message", "data": payload},
        )

    @staticmethod
    def notify_org_admins(org, notification_type, title, body="", data=None):
        """Broadcast a notification to all org admins/owners."""
        from apps.tenants.models import Membership
        from apps.core.models import ROLE_ADMIN

        members = Membership.objects.filter(
            organization=org, role__in=["owner", "admin"]
        ).select_related("user")
        for m in members:
            NotificationService.notify(
                user=m.user,
                org=org,
                notification_type=notification_type,
                title=title,
                body=body,
                data=data or {},
            )

    @staticmethod
    def _get_prefs(user, org):
        from apps.notifications.models import NotificationPreference
        return NotificationPreference.objects.filter(user=user, org=org).first()
