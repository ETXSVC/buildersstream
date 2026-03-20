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

        # Push via Web Push to registered browser subscriptions
        try:
            NotificationService.send_web_push(user, title=title, body=body, url=data.get("url", "/"))
        except Exception:
            logger.exception("Failed to send web push for notification %s", notif.pk)

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
    def send_web_push(user, title: str, body: str = "", url: str = "/"):
        """Send a Web Push notification to all of the user's registered subscriptions."""
        from django.conf import settings
        from apps.integrations.models import PushSubscription

        vapid_private_key = getattr(settings, "VAPID_PRIVATE_KEY", "")
        vapid_claims_email = getattr(settings, "VAPID_CLAIMS_EMAIL", "")
        if not vapid_private_key:
            return

        subscriptions = PushSubscription.objects.filter(user=user)
        if not subscriptions.exists():
            return

        try:
            from pywebpush import webpush, WebPushException
        except ImportError:
            logger.warning("pywebpush not installed — skipping web push")
            return

        import json
        payload = json.dumps({"title": title, "body": body, "url": url, "tag": "builderstream"})
        stale_ids = []

        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=payload,
                    vapid_private_key=vapid_private_key,
                    vapid_claims={"sub": f"mailto:{vapid_claims_email}"},
                )
            except WebPushException as exc:
                response = getattr(exc, "response", None)
                status = getattr(response, "status_code", None) if response else None
                if status in (404, 410):
                    stale_ids.append(sub.pk)
                else:
                    logger.warning("Web push failed for sub %s: %s", sub.pk, exc)
            except Exception as exc:
                logger.warning("Web push error for sub %s: %s", sub.pk, exc)

        if stale_ids:
            PushSubscription.objects.filter(pk__in=stale_ids).delete()

    @staticmethod
    def _get_prefs(user, org):
        from apps.notifications.models import NotificationPreference
        return NotificationPreference.objects.filter(user=user, org=org).first()
