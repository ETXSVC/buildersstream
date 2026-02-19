"""Admin registration for Integration Ecosystem models."""
from django.contrib import admin

from .models import APIKey, IntegrationConnection, SyncLog, WebhookEndpoint


class SyncLogInline(admin.TabularInline):
    model = SyncLog
    extra = 0
    readonly_fields = ["sync_type", "status", "records_synced", "records_failed", "started_at", "completed_at"]
    can_delete = False


@admin.register(IntegrationConnection)
class IntegrationConnectionAdmin(admin.ModelAdmin):
    list_display = ["integration_type", "organization", "status", "last_sync_at", "token_expires_at"]
    list_filter = ["integration_type", "status"]
    search_fields = ["organization__name"]
    readonly_fields = ["last_sync_at", "token_expires_at", "last_error", "created_at", "updated_at"]
    inlines = [SyncLogInline]


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ["connection", "sync_type", "status", "records_synced", "records_failed", "started_at"]
    list_filter = ["sync_type", "status"]
    readonly_fields = ["started_at", "completed_at"]


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ["url", "organization", "is_active", "failure_count", "last_triggered_at"]
    list_filter = ["is_active"]
    search_fields = ["url", "organization__name"]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "key_prefix", "is_active", "last_used_at", "expires_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "organization__name", "key_prefix"]
    readonly_fields = ["key_prefix", "key_hash", "last_used_at", "created_at"]
