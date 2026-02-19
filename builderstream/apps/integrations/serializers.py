"""Integration Ecosystem serializers."""
from rest_framework import serializers

from .models import APIKey, IntegrationConnection, SyncLog, WebhookEndpoint


class IntegrationConnectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationConnection
        fields = [
            "id", "integration_type", "status", "last_sync_at",
            "token_expires_at", "is_connected", "created_at",
        ]
        read_only_fields = ["id", "is_connected", "created_at"]


class IntegrationConnectionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationConnection
        fields = [
            "id", "integration_type", "status", "sync_config",
            "last_sync_at", "last_error", "token_expires_at",
            "is_connected", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "status", "last_sync_at", "last_error",
            "token_expires_at", "is_connected", "created_at", "updated_at",
        ]


class SyncLogSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = SyncLog
        fields = [
            "id", "connection", "sync_type", "status",
            "records_synced", "records_failed", "started_at",
            "completed_at", "duration_seconds", "error_details",
        ]
        read_only_fields = fields


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = [
            "id", "url", "events", "is_active",
            "last_triggered_at", "failure_count", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "last_triggered_at", "failure_count",
            "created_at", "updated_at",
        ]
        extra_kwargs = {
            "secret": {"write_only": True},
        }

    def create(self, validated_data):
        """Auto-generate secret if not provided."""
        instance = WebhookEndpoint(**validated_data)
        if not instance.secret:
            instance.generate_secret()
        instance.save()
        return instance


class APIKeyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            "id", "name", "key_prefix", "scopes",
            "rate_limit_per_hour", "last_used_at",
            "expires_at", "is_active", "created_at",
        ]
        read_only_fields = ["id", "key_prefix", "last_used_at", "created_at"]


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Used only on POST — returns the raw key once."""
    raw_key = serializers.CharField(read_only=True)

    class Meta:
        model = APIKey
        fields = [
            "id", "name", "scopes", "rate_limit_per_hour",
            "expires_at", "raw_key",
        ]
        read_only_fields = ["id", "raw_key"]

    def create(self, validated_data):
        prefix, raw_key = APIKey.generate_key()
        instance = APIKey(
            key_prefix=prefix,
            key_hash=APIKey.hash_key(raw_key),
            **validated_data,
        )
        instance.save()
        instance.raw_key = raw_key  # attach for single-response exposure
        return instance


class APIKeyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            "id", "name", "key_prefix", "scopes",
            "rate_limit_per_hour", "last_used_at",
            "expires_at", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "key_prefix", "last_used_at",
            "created_at", "updated_at",
        ]
