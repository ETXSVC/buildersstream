"""
Team Channels + Direct Messaging models.

Channel  ─── Message ─── MessageReaction
         └── ReadReceipt
"""
import uuid
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel, TimeStampedModel


class Channel(TenantModel):
    """A chat channel — public, private, or a DM between two users."""

    class ChannelType(models.TextChoices):
        PUBLIC = "public", "Public"
        PRIVATE = "private", "Private"
        DIRECT = "direct", "Direct Message"

    name = models.CharField(max_length=100, blank=True)  # blank for DM channels
    description = models.TextField(blank=True)
    channel_type = models.CharField(
        max_length=10, choices=ChannelType.choices, default=ChannelType.PUBLIC
    )
    slug = models.SlugField(max_length=110, blank=True)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="channels",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="joined_channels",
        blank=True,
    )
    is_archived = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "channel_type"], name="collab_ch_org_type_idx"),
            models.Index(fields=["organization", "slug"], name="collab_ch_org_slug_idx"),
        ]
        unique_together = [("organization", "slug")]

    def __str__(self):
        return self.name or f"DM-{self.pk}"


class Message(TenantModel):
    """A single message posted in a channel."""

    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="messages"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="chat_messages",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    content = models.TextField()
    content_json = models.JSONField(default=dict, blank=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    attachments = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["channel", "created_at"], name="collab_msg_ch_created_idx"),
            models.Index(fields=["channel", "parent"], name="collab_msg_ch_parent_idx"),
        ]

    def __str__(self):
        return f"Message({self.pk}) in {self.channel_id}"


class MessageReaction(TimeStampedModel):
    """Emoji reaction to a message."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="message_reactions",
    )
    emoji = models.CharField(max_length=10)

    class Meta:
        unique_together = [("message", "user", "emoji")]
        indexes = [
            models.Index(fields=["message", "emoji"], name="collab_rxn_msg_emoji_idx"),
        ]


class ReadReceipt(TimeStampedModel):
    """Tracks the last message a user has read in a channel."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="read_receipts"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="read_receipts",
    )
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("channel", "user")]
        indexes = [
            models.Index(fields=["channel", "user"], name="collab_rr_ch_user_idx"),
        ]
