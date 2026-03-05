"""
Notification model — in-app notifications delivered via WebSocket or stored
for later retrieval.  All notifications are tenant-scoped via TenantModel.
"""
from django.db import models

from apps.core.models import TenantModel


class Notification(TenantModel):
    class NotificationType(models.TextChoices):
        # Project events
        PROJECT_STATUS_CHANGED = "project_status_changed", "Project Status Changed"
        PROJECT_HEALTH_ALERT = "project_health_alert", "Project Health Alert"
        # Action items / tasks
        ACTION_ITEM_ASSIGNED = "action_item_assigned", "Action Item Assigned"
        ACTION_ITEM_DUE = "action_item_due", "Action Item Due"
        # Document events
        RFI_SUBMITTED = "rfi_submitted", "RFI Submitted"
        RFI_RESPONSE = "rfi_response", "RFI Response"
        SUBMITTAL_RESPONSE = "submittal_response", "Submittal Response"
        DOCUMENT_UPLOADED = "document_uploaded", "Document Uploaded"
        # Financial events
        INVOICE_SENT = "invoice_sent", "Invoice Sent"
        INVOICE_PAID = "invoice_paid", "Invoice Paid"
        CHANGE_ORDER_SUBMITTED = "change_order_submitted", "Change Order Submitted"
        CHANGE_ORDER_APPROVED = "change_order_approved", "Change Order Approved"
        # Field ops
        DAILY_LOG_SUBMITTED = "daily_log_submitted", "Daily Log Submitted"
        CLOCK_IN = "clock_in", "Clock In"
        # Safety
        INCIDENT_REPORTED = "incident_reported", "Incident Reported"
        INSPECTION_DUE = "inspection_due", "Inspection Due"
        # CRM / proposals
        PROPOSAL_VIEWED = "proposal_viewed", "Proposal Viewed"
        PROPOSAL_SIGNED = "proposal_signed", "Proposal Signed"
        LEAD_ASSIGNED = "lead_assigned", "Lead Assigned"
        # Service
        SERVICE_TICKET_CREATED = "service_ticket_created", "Service Ticket Created"
        SERVICE_TICKET_UPDATED = "service_ticket_updated", "Service Ticket Updated"
        # Generic / system
        MENTION = "mention", "Mention"
        SYSTEM = "system", "System"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    recipient = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    # JSON payload for the frontend (e.g. link, entity id)
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "recipient", "-created_at"], name="notif_org_recip_idx"),
            models.Index(fields=["organization", "recipient", "is_read"], name="notif_org_recip_read_idx"),
        ]

    def __str__(self):
        return f"{self.notification_type} → {self.recipient_id}"


class NotificationPreference(TenantModel):
    """Per-user per-type preferences: in-app, email, push."""

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    # Global toggles
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=False)
    # Quiet hours (UTC)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    # Per-type overrides as JSON: {"project_status_changed": {"in_app": true, "email": false}}
    type_overrides = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "user"], name="notifpref_org_user_idx"),
        ]

    def __str__(self):
        return f"Preferences for {self.user_id}"
