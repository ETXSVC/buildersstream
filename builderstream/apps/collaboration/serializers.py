"""Collaboration app serializers."""
from rest_framework import serializers

from .models import Channel, Message, MessageReaction, ReadReceipt


class MessageReactionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = MessageReaction
        fields = ["id", "message", "user", "user_name", "emoji", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email if obj.user else None


class MessageSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id", "channel", "author", "author_name",
            "parent", "content", "is_edited", "edited_at",
            "is_deleted", "attachments", "reactions", "reply_count",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "author", "is_edited", "edited_at", "is_deleted",
            "reactions", "reply_count", "created_at", "updated_at",
        ]

    def get_author_name(self, obj):
        if obj.is_deleted:
            return None
        return obj.author.get_full_name() or obj.author.email if obj.author else None

    def get_reactions(self, obj):
        from django.db.models import Count
        return list(
            obj.reactions.values("emoji").annotate(count=Count("id"))
        )

    def get_reply_count(self, obj):
        return obj.replies.filter(is_deleted=False).count()


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["channel", "parent", "content", "attachments"]


class ChannelSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = [
            "id", "name", "description", "channel_type", "slug",
            "project", "is_archived", "members_count", "unread_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "members_count", "unread_count", "created_at", "updated_at"]

    def get_members_count(self, obj):
        return obj.members.count()

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return 0
        receipt = obj.read_receipts.filter(user=request.user).first()
        if receipt is None:
            return obj.messages.filter(is_deleted=False).count()
        return obj.messages.filter(
            is_deleted=False, created_at__gt=receipt.last_read_at
        ).count()


class ChannelCreateSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = Channel
        fields = ["name", "description", "channel_type", "project", "member_ids"]

    def create(self, validated_data):
        member_ids = validated_data.pop("member_ids", [])
        channel = super().create(validated_data)
        if member_ids:
            from apps.accounts.models import User
            members = User.objects.filter(pk__in=member_ids)
            channel.members.set(members)
        # Always add creator as member
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            channel.members.add(request.user)
        return channel


class ReadReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadReceipt
        fields = ["id", "channel", "user", "last_read_at"]
        read_only_fields = ["id", "user", "last_read_at"]
