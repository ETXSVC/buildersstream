"""Collaboration app ViewSets."""
from django.utils.text import slugify
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSetMixin

from .models import Channel, Message, ReadReceipt
from .serializers import (
    ChannelCreateSerializer,
    ChannelSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)


class ChannelViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD + member management for channels."""

    serializer_class = ChannelSerializer
    filterset_fields = ["channel_type", "project", "is_archived"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        # Allow ?is_archived=true to list archived channels for the restore UI.
        want_archived = self.request.query_params.get("is_archived", "false").lower() == "true"
        qs = Channel.objects.filter(is_archived=want_archived)
        user = self.request.user
        from apps.tenants.models import OrganizationMembership
        org = getattr(self.request, "organization", None)
        if org:
            membership = OrganizationMembership.objects.filter(
                organization=org, user=user
            ).first()
            admin_roles = {"owner", "admin"}
            if membership and membership.role not in admin_roles:
                qs = qs.filter(members=user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return ChannelCreateSerializer
        return ChannelSerializer

    def perform_create(self, serializer):
        name = serializer.validated_data.get("name", "")
        slug = slugify(name) if name else ""
        serializer.save(slug=slug)

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        channel = self.get_object()
        if channel.channel_type == Channel.ChannelType.DIRECT:
            return Response({"detail": "Cannot join a DM channel."}, status=400)
        channel.members.add(request.user)
        return Response({"detail": "Joined."})

    @action(detail=True, methods=["post"], url_path="leave")
    def leave(self, request, pk=None):
        channel = self.get_object()
        channel.members.remove(request.user)
        return Response({"detail": "Left."})

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id required."}, status=400)
        from apps.accounts.models import User
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
        channel.members.add(user)
        return Response({"detail": "Member added."})

    @action(detail=True, methods=["post"], url_path="remove-member")
    def remove_member(self, request, pk=None):
        channel = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id required."}, status=400)
        from apps.accounts.models import User
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
        channel.members.remove(user)
        return Response({"detail": "Member removed."})

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        channel = self.get_object()
        channel.is_archived = True
        channel.save(update_fields=["is_archived"])
        return Response({"detail": "Archived."})

    @action(detail=True, methods=["post"], url_path="unarchive")
    def unarchive(self, request, pk=None):
        # get_object() only searches is_archived=False by default; bypass that.
        from django.shortcuts import get_object_or_404
        org = getattr(request, "organization", None)
        channel = get_object_or_404(Channel, pk=pk, organization=org, is_archived=True)
        channel.is_archived = False
        channel.save(update_fields=["is_archived"])
        return Response({"detail": "Restored."})

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        channel = self.get_object()
        ReadReceipt.objects.update_or_create(
            channel=channel, user=request.user, defaults={}
        )
        return Response({"detail": "Marked as read."})

    @action(detail=False, methods=["post"], url_path="direct")
    def create_direct(self, request):
        """Create or retrieve an existing DM channel between two users."""
        other_user_id = request.data.get("user_id")
        if not other_user_id:
            return Response({"detail": "user_id required."}, status=400)
        from apps.accounts.models import User
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        org = request.organization
        existing = (
            Channel.objects.filter(
                organization=org,
                channel_type=Channel.ChannelType.DIRECT,
                members=request.user,
            )
            .filter(members=other_user)
            .first()
        )
        if existing:
            return Response(ChannelSerializer(existing, context={"request": request}).data)

        # Build a deterministic slug from both user IDs so it's always unique
        import uuid
        ids = sorted([str(request.user.pk), str(other_user.pk)])
        slug = f"dm-{uuid.uuid5(uuid.NAMESPACE_DNS, '-'.join(ids))}"
        channel = Channel.objects.create(
            organization=org,
            channel_type=Channel.ChannelType.DIRECT,
            name="",
            slug=slug,
        )
        channel.members.set([request.user, other_user])
        return Response(
            ChannelSerializer(channel, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class MessageViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for channel messages."""

    serializer_class = MessageSerializer
    filterset_fields = ["channel", "parent"]
    ordering = ["created_at"]

    def get_queryset(self):
        qs = Message.objects.select_related("author", "channel")
        channel_id = self.request.query_params.get("channel")
        if channel_id:
            qs = qs.filter(channel_id=channel_id)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        org = self.request.organization
        serializer.save(organization=org, author=self.request.user)

    def perform_update(self, serializer):
        from django.utils import timezone
        serializer.save(is_edited=True, edited_at=timezone.now())

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.content = "[deleted]"
        instance.save(update_fields=["is_deleted", "content"])

    @action(detail=True, methods=["get"], url_path="replies")
    def replies(self, request, pk=None):
        msg = self.get_object()
        replies = msg.replies.filter(is_deleted=False).order_by("created_at")
        page = self.paginate_queryset(replies)
        if page is not None:
            return self.get_paginated_response(
                MessageSerializer(page, many=True, context={"request": request}).data
            )
        return Response(
            MessageSerializer(replies, many=True, context={"request": request}).data
        )
