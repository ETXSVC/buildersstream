from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "priority", "title", "body",
            "data", "is_read", "read_at", "created_at",
        ]
        read_only_fields = ["id", "created_at", "read_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "id", "in_app_enabled", "email_enabled", "push_enabled",
            "quiet_hours_start", "quiet_hours_end", "type_overrides",
        ]
