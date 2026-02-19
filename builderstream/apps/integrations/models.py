"""Integration Ecosystem & Open API models."""
import hashlib
import secrets
from django.db import models

from apps.core.models import TenantModel


class IntegrationConnection(TenantModel):
    """OAuth/API connection to an external service."""

    class IntegrationType(models.TextChoices):
        QUICKBOOKS_ONLINE = "quickbooks_online", "QuickBooks Online"
        QUICKBOOKS_DESKTOP = "quickbooks_desktop", "QuickBooks Desktop"
        XERO = "xero", "Xero"
        GOOGLE_WORKSPACE = "google_workspace", "Google Workspace"
        MICROSOFT_365 = "microsoft_365", "Microsoft 365"
        STRIPE_CONNECT = "stripe_connect", "Stripe Connect"
        WEATHER_API = "weather_api", "Weather API"

    class Status(models.TextChoices):
        CONNECTED = "connected", "Connected"
        DISCONNECTED = "disconnected", "Disconnected"
        ERROR = "error", "Error"
        SYNCING = "syncing", "Syncing"

    integration_type = models.CharField(max_length=30, choices=IntegrationType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISCONNECTED)
    access_token_encrypted = models.TextField(blank=True)
    refresh_token_encrypted = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    sync_config = models.JSONField(default=dict, blank=True)
    connected_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="integration_connections",
    )

    class Meta:
        ordering = ["integration_type"]
        indexes = [
            models.Index(fields=["organization", "integration_type"], name="integ_conn_org_type_idx"),
            models.Index(fields=["organization", "status"], name="integ_conn_org_status_idx"),
        ]
        unique_together = [["organization", "integration_type"]]

    def __str__(self):
        return f"{self.get_integration_type_display()} ({self.organization})"

    @property
    def is_connected(self):
        return self.status == self.Status.CONNECTED


class SyncLog(TenantModel):
    """Audit log for integration sync operations."""

    class SyncType(models.TextChoices):
        FULL = "full", "Full Sync"
        INCREMENTAL = "incremental", "Incremental"
        MANUAL = "manual", "Manual"

    class Status(models.TextChoices):
        STARTED = "started", "Started"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PARTIAL = "partial", "Partial"

    connection = models.ForeignKey(
        IntegrationConnection,
        on_delete=models.CASCADE,
        related_name="sync_logs",
    )
    sync_type = models.CharField(max_length=20, choices=SyncType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.STARTED)
    records_synced = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_details = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["connection", "-started_at"], name="integ_synclog_conn_at_idx"),
            models.Index(fields=["organization", "status"], name="integ_synclog_org_status_idx"),
        ]

    def __str__(self):
        return f"{self.connection} sync @ {self.started_at}"

    @property
    def duration_seconds(self):
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class WebhookEndpoint(TenantModel):
    """Registered webhook endpoint for outbound event delivery."""

    url = models.URLField(max_length=500)
    events = models.JSONField(default=list, blank=True)
    secret = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    failure_count = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "is_active"], name="integ_webhook_org_active_idx"),
        ]

    def __str__(self):
        return f"Webhook → {self.url}"

    def generate_secret(self):
        """Generate a new HMAC secret."""
        self.secret = secrets.token_hex(32)

    def has_event(self, event_type):
        """Check if this endpoint is subscribed to an event type."""
        return not self.events or event_type in self.events


class APIKey(TenantModel):
    """API key for programmatic access to the public API."""

    name = models.CharField(max_length=100)
    key_prefix = models.CharField(max_length=16)  # visible prefix (e.g. "bsp_abcdef01")
    key_hash = models.CharField(max_length=64)    # SHA-256 hash of full key
    scopes = models.JSONField(default=list, blank=True)
    rate_limit_per_hour = models.IntegerField(default=1000)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="api_keys",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["key_prefix"], name="integ_apikey_prefix_idx"),
            models.Index(fields=["organization", "is_active"], name="integ_apikey_org_active_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    @staticmethod
    def hash_key(raw_key):
        """Return SHA-256 hex digest of the raw key."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    @staticmethod
    def generate_key():
        """Return (prefix, raw_key) for a new API key."""
        prefix = "bsp_" + secrets.token_hex(4)   # 8-char prefix with "bsp_" + 4 bytes
        secret = secrets.token_urlsafe(32)
        raw_key = f"{prefix}_{secret}"
        return prefix, raw_key

    def has_scope(self, scope):
        """Check if this key has the required scope."""
        return not self.scopes or scope in self.scopes
