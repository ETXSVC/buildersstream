from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient", "notification_type", "priority", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "priority", "is_read"]
    search_fields = ["recipient__email", "title", "body"]
    readonly_fields = ["created_at", "read_at"]
    ordering = ["-created_at"]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "in_app_enabled", "email_enabled", "push_enabled"]
    search_fields = ["user__email"]
