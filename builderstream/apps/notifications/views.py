from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSetMixin
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationViewSet(TenantViewSetMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    filterset_fields = ["is_read", "notification_type", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Notification.objects.filter(
            org=self.request.organization,
            recipient=self.request.user,
        )

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({"status": "ok"})

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        if not notif.is_read:
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read", "read_at"])
        return Response(NotificationSerializer(notif).data)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})


class NotificationPreferenceViewSet(TenantViewSetMixin, viewsets.GenericViewSet):
    serializer_class = NotificationPreferenceSerializer

    def get_queryset(self):
        return NotificationPreference.objects.filter(
            org=self.request.organization,
            user=self.request.user,
        )

    @action(detail=False, methods=["get", "put", "patch"], url_path="me")
    def me(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(
            org=request.organization,
            user=request.user,
        )
        if request.method == "GET":
            return Response(NotificationPreferenceSerializer(prefs).data)

        serializer = NotificationPreferenceSerializer(
            prefs, data=request.data, partial=(request.method == "PATCH")
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
