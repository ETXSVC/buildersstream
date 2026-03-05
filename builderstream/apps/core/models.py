"""Core abstract models for the BuilderStream platform."""
import uuid

from django.conf import settings
from django.db import models

# Role hierarchy constants (also referenced in permissions.py)
ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TenantManager(models.Manager):
    """Manager that auto-filters querysets by organization via thread-local context."""

    def get_queryset(self):
        qs = super().get_queryset()
        from apps.tenants.context import get_current_organization

        current_org = get_current_organization()
        if current_org is not None:
            qs = qs.filter(organization=current_org)
        return qs

    def for_organization(self, organization):
        """Explicit filter — bypasses thread-local and filters directly."""
        return super().get_queryset().filter(organization=organization)

    def unscoped(self):
        """Return queryset without tenant filtering (for admin/system use)."""
        return super().get_queryset()


class TenantModel(TimeStampedModel):
    """Abstract base model for multi-tenant resources.

    Extends TimeStampedModel with an organization FK and
    a custom manager that auto-filters by the current organization
    from thread-local storage.
    """

    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )

    objects = TenantManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Auto-set organization from thread-local if not already set."""
        if not self.organization_id:
            from apps.tenants.context import get_current_organization

            current_org = get_current_organization()
            if current_org is not None:
                self.organization = current_org
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# AuditLog — append-only table for security-relevant events
# ---------------------------------------------------------------------------

class AuditLog(TimeStampedModel):
    """Immutable audit log for all security-relevant actions.

    Stored in the `core` app rather than `accounts` so all apps can write
    to it without circular imports.  Never updated or deleted.
    """

    class Action(models.TextChoices):
        LOGIN = "login", "Login"
        LOGIN_FAILED = "login_failed", "Login Failed"
        LOGOUT = "logout", "Logout"
        PASSWORD_CHANGED = "password_changed", "Password Changed"
        TWO_FACTOR_ENABLED = "2fa_enabled", "2FA Enabled"
        TWO_FACTOR_DISABLED = "2fa_disabled", "2FA Disabled"
        TWO_FACTOR_FAILED = "2fa_failed", "2FA Code Failed"
        USER_CREATED = "user_created", "User Created"
        USER_UPDATED = "user_updated", "User Updated"
        USER_DELETED = "user_deleted", "User Deleted"
        ORG_SETTINGS_CHANGED = "org_settings_changed", "Org Settings Changed"
        MEMBER_INVITED = "member_invited", "Member Invited"
        MEMBER_REMOVED = "member_removed", "Member Removed"
        ROLE_CHANGED = "role_changed", "Role Changed"
        EXPORT = "export", "Data Export"
        API_KEY_CREATED = "api_key_created", "API Key Created"
        API_KEY_REVOKED = "api_key_revoked", "API Key Revoked"
        PERMISSION_DENIED = "permission_denied", "Permission Denied"

    # May be null for anonymous actions (failed login attempts)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    org = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    # Flexible payload — store relevant IDs, old/new values, etc.
    details = models.JSONField(default=dict, blank=True)
    # The HTTP request path that triggered this event
    path = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["org", "-created_at"], name="auditlog_org_created_idx"),
            models.Index(fields=["user", "-created_at"], name="auditlog_user_created_idx"),
            models.Index(fields=["action", "-created_at"], name="auditlog_action_created_idx"),
            models.Index(fields=["ip_address", "-created_at"], name="auditlog_ip_created_idx"),
        ]

    def __str__(self):
        return f"{self.action} | {self.user_id} | {self.created_at}"

    @classmethod
    def log(cls, action, user=None, org=None, ip_address=None,
            user_agent="", details=None, path=""):
        """Convenience factory — never raises, logs errors gracefully."""
        try:
            return cls.objects.create(
                action=action,
                user=user,
                org=org,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                path=path,
            )
        except Exception:
            import logging
            logging.getLogger(__name__).exception("AuditLog.log failed")
            return None


# ---------------------------------------------------------------------------
# IPWhitelist — per-org IP allowlists for admin access
# ---------------------------------------------------------------------------

class IPWhitelist(TimeStampedModel):
    """Allowed IP CIDR ranges for an organization's admin operations."""

    org = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="ip_whitelist",
    )
    cidr = models.CharField(max_length=50)  # e.g. "192.168.1.0/24" or "10.0.0.1"
    label = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["org", "cidr"]
        indexes = [
            models.Index(fields=["org", "is_active"], name="ipwhitelist_org_active_idx"),
        ]

    def __str__(self):
        return f"{self.org_id} | {self.cidr}"


# ---------------------------------------------------------------------------
# UserSession — tracks active JWT sessions (for session management UI)
# ---------------------------------------------------------------------------

class UserSession(TimeStampedModel):
    """Track JWT refresh tokens per device so users can revoke sessions."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    jti = models.CharField(max_length=255, unique=True, db_index=True)  # JWT token ID
    device_name = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-last_active"]
        indexes = [
            models.Index(fields=["user", "is_active"], name="usersession_user_active_idx"),
        ]

    def __str__(self):
        return f"{self.user_id} | {self.device_name or 'Unknown'}"
