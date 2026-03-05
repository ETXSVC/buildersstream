"""
ChatConsumer — WebSocket handler for a single channel room.

ws/collaboration/channels/{channel_id}/?token=<jwt>
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        self.group_name = f"chat_{self.channel_id}"

        user = await self._authenticate()
        if user is None:
            await self.close(code=4001)
            return

        # Verify membership
        is_member = await self._check_membership(user, self.channel_id)
        if not is_member:
            await self.close(code=4003)
            return

        self.user = user
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self._update_read_receipt()
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            return

        action = data.get("type")
        if action == "message.send":
            await self._handle_send(data)
        elif action == "message.edit":
            await self._handle_edit(data)
        elif action == "message.delete":
            await self._handle_delete(data)
        elif action == "reaction.toggle":
            await self._handle_reaction(data)
        elif action == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.typing",
                    "user_id": str(self.user.pk),
                    "user_name": self.user.get_full_name() or self.user.email,
                },
            )

    # ── Group message handlers ──────────────────────────────────────── #

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({"type": "typing", **event}))

    # ── Actions ─────────────────────────────────────────────────────── #

    async def _handle_send(self, data):
        content = (data.get("content") or "").strip()
        if not content:
            return
        msg = await self._create_message(
            channel_id=self.channel_id,
            author=self.user,
            content=content,
            parent_id=data.get("parent_id"),
        )
        payload = await self._serialize_message(msg)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.message", "data": {"type": "message.new", **payload}},
        )

    async def _handle_edit(self, data):
        msg_id = data.get("message_id")
        content = (data.get("content") or "").strip()
        if not msg_id or not content:
            return
        msg = await self._edit_message(msg_id, self.user, content)
        if msg:
            payload = await self._serialize_message(msg)
            await self.channel_layer.group_send(
                self.group_name,
                {"type": "chat.message", "data": {"type": "message.edited", **payload}},
            )

    async def _handle_delete(self, data):
        msg_id = data.get("message_id")
        if not msg_id:
            return
        ok = await self._delete_message(msg_id, self.user)
        if ok:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.message",
                    "data": {"type": "message.deleted", "message_id": msg_id},
                },
            )

    async def _handle_reaction(self, data):
        msg_id = data.get("message_id")
        emoji = data.get("emoji", "")
        if not msg_id or not emoji:
            return
        reactions = await self._toggle_reaction(msg_id, self.user, emoji)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "data": {
                    "type": "reaction.updated",
                    "message_id": msg_id,
                    "reactions": reactions,
                },
            },
        )

    # ── DB helpers ──────────────────────────────────────────────────── #

    async def _authenticate(self):
        from apps.accounts.models import User
        qs = self.scope.get("query_string", b"").decode()
        params = dict(p.split("=") for p in qs.split("&") if "=" in p)
        token_str = params.get("token", "")
        if not token_str:
            return None
        try:
            token = AccessToken(token_str)
            return await database_sync_to_async(User.objects.get)(pk=token["user_id"])
        except (TokenError, Exception):
            return None

    @database_sync_to_async
    def _check_membership(self, user, channel_id):
        from .models import Channel
        return Channel.objects.filter(
            pk=channel_id, members=user
        ).exists()

    @database_sync_to_async
    def _create_message(self, channel_id, author, content, parent_id=None):
        from .models import Channel, Message
        channel = Channel.objects.get(pk=channel_id)
        return Message.objects.create(
            organization=channel.organization,
            channel=channel,
            author=author,
            content=content,
            parent_id=parent_id,
        )

    @database_sync_to_async
    def _edit_message(self, msg_id, user, content):
        from django.utils import timezone
        from .models import Message
        try:
            msg = Message.objects.get(pk=msg_id, author=user, is_deleted=False)
            msg.content = content
            msg.is_edited = True
            msg.edited_at = timezone.now()
            msg.save(update_fields=["content", "is_edited", "edited_at"])
            return msg
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def _delete_message(self, msg_id, user):
        from .models import Message
        updated = Message.objects.filter(pk=msg_id, author=user).update(
            is_deleted=True, content="[deleted]"
        )
        return updated > 0

    @database_sync_to_async
    def _toggle_reaction(self, msg_id, user, emoji):
        from .models import Message, MessageReaction
        try:
            reaction = MessageReaction.objects.get(message_id=msg_id, user=user, emoji=emoji)
            reaction.delete()
        except MessageReaction.DoesNotExist:
            MessageReaction.objects.create(message_id=msg_id, user=user, emoji=emoji)
        reactions = (
            MessageReaction.objects.filter(message_id=msg_id)
            .values("emoji")
            .annotate(count=models.Count("id"))
        )
        from django.db.models import Count
        reactions = list(
            MessageReaction.objects.filter(message_id=msg_id)
            .values("emoji")
            .annotate(count=Count("id"))
        )
        return [{"emoji": r["emoji"], "count": r["count"]} for r in reactions]

    @database_sync_to_async
    def _update_read_receipt(self):
        from .models import ReadReceipt
        ReadReceipt.objects.update_or_create(
            channel_id=self.channel_id, user=self.user,
            defaults={}
        )

    @database_sync_to_async
    def _serialize_message(self, msg):
        return {
            "id": str(msg.pk),
            "channel_id": str(msg.channel_id),
            "author_id": str(msg.author_id) if msg.author_id else None,
            "author_name": msg.author.get_full_name() or msg.author.email if msg.author else "Unknown",
            "parent_id": str(msg.parent_id) if msg.parent_id else None,
            "content": msg.content,
            "is_edited": msg.is_edited,
            "created_at": msg.created_at.isoformat(),
        }
