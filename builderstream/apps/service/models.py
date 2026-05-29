"""Service & Warranty Management models."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class ServiceTicket(TenantModel):
    """Service/warranty/maintenance ticket with full billing and dispatch support."""

    class Priority(models.TextChoices):
        EMERGENCY = "emergency", "Emergency"
        HIGH = "high", "High"
        NORMAL = "normal", "Normal"
        LOW = "low", "Low"

    class Status(models.TextChoices):
        NEW = "new", "New"
        ASSIGNED = "assigned", "Assigned"
        IN_PROGRESS = "in_progress", "In Progress"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CLOSED = "closed", "Closed"

    class TicketType(models.TextChoices):
        WARRANTY = "warranty", "Warranty"
        SERVICE_CALL = "service_call", "Service Call"
        MAINTENANCE = "maintenance", "Scheduled Maintenance"
        CALLBACK = "callback", "Callback"
        EMERGENCY = "emergency", "Emergency"

    class BillingType(models.TextChoices):
        TIME_AND_MATERIAL = "time_and_material", "Time & Material"
        FLAT_RATE = "flat_rate", "Flat Rate"
        WARRANTY_NO_CHARGE = "warranty_no_charge", "Warranty (No Charge)"

    # Core fields
    ticket_number = models.CharField(max_length=30, blank=True, db_index=True)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        related_name="service_tickets",
        null=True,
        blank=True,
    )
    client = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        related_name="service_tickets",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.NORMAL
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW
    )
    ticket_type = models.CharField(
        max_length=20, choices=TicketType.choices, default=TicketType.SERVICE_CALL
    )

    # Assignment & scheduling
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_service_tickets",
    )
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    resolution = models.TextField(blank=True)

    # Billing
    billable = models.BooleanField(default=True)
    billing_type = models.CharField(
        max_length=30,
        choices=BillingType.choices,
        default=BillingType.TIME_AND_MATERIAL,
    )
    labor_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    invoice = models.ForeignKey(
        "financials.Invoice",
        on_delete=models.SET_NULL,
        related_name="service_tickets",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"], name="svc_ticket_org_status_idx"),
            models.Index(fields=["organization", "priority"], name="svc_ticket_org_priority_idx"),
            models.Index(fields=["organization", "-created_at"], name="svc_ticket_org_created_idx"),
            models.Index(fields=["assigned_to", "status"], name="svc_ticket_assignee_status_idx"),
        ]

    def __str__(self):
        return f"{self.ticket_number} – {self.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_number and self.organization_id:
            from django.utils import timezone
            year = timezone.now().year
            last = (
                ServiceTicket.objects.filter(
                    organization_id=self.organization_id,
                    ticket_number__startswith=f"SVC-{year}-",
                )
                .order_by("ticket_number")
                .last()
            )
            if last and last.ticket_number:
                try:
                    seq = int(last.ticket_number.rsplit("-", 1)[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
            self.ticket_number = f"SVC-{year}-{seq:04d}"
        super().save(*args, **kwargs)


class Warranty(TenantModel):
    """Warranty record for a completed project (workmanship, manufacturer, extended)."""

    class WarrantyType(models.TextChoices):
        WORKMANSHIP = "workmanship", "Workmanship"
        MANUFACTURER = "manufacturer", "Manufacturer"
        EXTENDED = "extended", "Extended"

    class WarrantyStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CLAIMED = "claimed", "Claimed"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="warranties",
    )
    warranty_type = models.CharField(
        max_length=20, choices=WarrantyType.choices, default=WarrantyType.WORKMANSHIP
    )
    description = models.CharField(max_length=255)
    coverage_details = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    manufacturer = models.CharField(max_length=255, blank=True)
    product_info = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=WarrantyStatus.choices, default=WarrantyStatus.ACTIVE
    )

    class Meta:
        ordering = ["end_date"]
        indexes = [
            models.Index(fields=["organization", "status"], name="svc_warranty_org_status_idx"),
            models.Index(fields=["organization", "end_date"], name="svc_warranty_org_end_idx"),
            models.Index(fields=["project", "warranty_type"], name="svc_warranty_proj_type_idx"),
        ]

    def __str__(self):
        return f"{self.get_warranty_type_display()} – {self.description}"

    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == self.WarrantyStatus.ACTIVE and self.end_date >= timezone.now().date()


class WarrantyClaim(TenantModel):
    """A claim filed against an existing warranty."""

    class ClaimStatus(models.TextChoices):
        FILED = "filed", "Filed"
        IN_REVIEW = "in_review", "In Review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        RESOLVED = "resolved", "Resolved"

    warranty = models.ForeignKey(
        Warranty,
        on_delete=models.CASCADE,
        related_name="claims",
    )
    service_ticket = models.ForeignKey(
        ServiceTicket,
        on_delete=models.SET_NULL,
        related_name="warranty_claims",
        null=True,
        blank=True,
    )
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=ClaimStatus.choices, default=ClaimStatus.FILED
    )
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    resolution = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"], name="svc_wclm_org_status_idx"),
            models.Index(fields=["warranty", "status"], name="svc_wclm_warranty_status_idx"),
        ]

    def __str__(self):
        return f"Claim on {self.warranty} ({self.get_status_display()})"


class ServiceAgreement(TenantModel):
    """Recurring maintenance / service agreement with a client."""

    class AgreementType(models.TextChoices):
        MAINTENANCE = "maintenance", "Maintenance"
        INSPECTION = "inspection", "Inspection"
        FULL_SERVICE = "full_service", "Full Service"

    class BillingFrequency(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"

    class AgreementStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Canceled"

    client = models.ForeignKey(
        "crm.Contact",
        on_delete=models.CASCADE,
        related_name="service_agreements",
    )
    name = models.CharField(max_length=255)
    agreement_type = models.CharField(
        max_length=20, choices=AgreementType.choices, default=AgreementType.MAINTENANCE
    )
    start_date = models.DateField()
    end_date = models.DateField()
    billing_frequency = models.CharField(
        max_length=20, choices=BillingFrequency.choices, default=BillingFrequency.MONTHLY
    )
    billing_amount = models.DecimalField(max_digits=12, decimal_places=2)
    visits_per_year = models.PositiveIntegerField(default=12)
    visits_completed = models.PositiveIntegerField(default=0)
    auto_renew = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20, choices=AgreementStatus.choices, default=AgreementStatus.ACTIVE
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["end_date"]
        indexes = [
            models.Index(fields=["organization", "status"], name="svc_agree_org_status_idx"),
            models.Index(fields=["organization", "end_date"], name="svc_agree_org_end_idx"),
            models.Index(fields=["client", "status"], name="svc_agree_client_status_idx"),
        ]

    def __str__(self):
        return f"{self.name} – {self.client}"

    @property
    def visits_remaining(self):
        return max(0, self.visits_per_year - self.visits_completed)
