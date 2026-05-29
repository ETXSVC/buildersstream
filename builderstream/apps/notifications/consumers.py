"""
WebSocket consumer for real-time notifications.

Connection URL: ws://host/ws/notifications/
Auth: JWTCookieAuthMiddleware sets scope['user'] from the 'bs_access' HttpOnly cookie.

Each user is placed in their own channel group: "user_{user_id}"
Messages are broadcast via NotificationService.send_to_user().
"""
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user is None or isinstance(user, AnonymousUser):
            await self.accept()
            await self.close(code=4001)
            return

        self.user = user
        self.group_name = f"user_{user.pk}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send unread count on connect
        unread = await self._get_unread_count(user)
        await self.send(text_data=json.dumps({"type": "unread_count", "count": unread}))

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Handle messages from client (e.g. mark-read commands)."""
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return

        action = data.get("action")
        if action == "mark_read":
            notification_id = data.get("id")
            if notification_id:
                await self._mark_read(notification_id)
                unread = await self._get_unread_count(self.user)
                await self.send(text_data=json.dumps({"type": "unread_count", "count": unread}))
        elif action == "mark_all_read":
            await self._mark_all_read()
            await self.send(text_data=json.dumps({"type": "unread_count", "count": 0}))

    # ------------------------------------------------------------------ #
    # Group message handlers (called by channel layer)
    # ------------------------------------------------------------------ #

    async def notification_message(self, event):
        """Receive from channel layer and forward to WebSocket."""
        await self.send(text_data=json.dumps(event["data"]))

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @database_sync_to_async
    def _get_unread_count(self, user):
        from apps.notifications.models import Notification
        return Notification.objects.filter(recipient=user, is_read=False).count()

    @database_sync_to_async
    def _mark_read(self, notification_id):
        from django.utils import timezone
        from apps.notifications.models import Notification
        Notification.objects.filter(
            pk=notification_id, recipient=self.user
        ).update(is_read=True, read_at=timezone.now())

    @database_sync_to_async
    def _mark_all_read(self):
        from django.utils import timezone
        from apps.notifications.models import Notification
        Notification.objects.filter(
            recipient=self.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
