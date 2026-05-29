"""
Client Collaboration Portal models.

7 models:
1. ClientPortalAccess  - Magic-link auth record per contact+project
2. Selection           - Material/finish decision needed from client
3. SelectionOption     - Individual choice within a Selection
4. ClientApproval      - Formal approval request (change orders, draws, etc.)
5. ClientMessage       - In-portal messaging between contractor and client
6. ClientSatisfactionSurvey - NPS/rating surveys triggered at milestones
7. PortalBranding      - Per-org white-label customization (OneToOne with Org)
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TenantModel


class ClientPortalAccess(TenantModel):
    """
    Grants a CRM Contact access to a specific project portal.

    Authentication is via a UUID magic link — the contact does NOT have a
    User account. Optionally protected by a PIN code for extra security.
    """

    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.CASCADE,
        related_name="portal_accesses",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="client_portal_accesses",
    )
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    email = models.EmailField(
        help_text="Portal login email — may differ from contact's primary email"
    )
    pin_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="Optional 4-6 digit PIN for extra portal security",
    )
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Granular permissions: view_photos, view_schedule, view_documents, make_payments, approve_selections, send_messages",
    )

    class Meta:
        db_table = "clients_portal_access"
        verbose_name = "Client Portal Access"
        verbose_name_plural = "Client Portal Accesses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "project"]),
            models.Index(fields=["organization", "contact"]),
            models.Index(fields=["access_token"]),
            models.Index(fields=["email"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "contact", "project"],
                name="unique_client_portal_access_per_project",
            ),
        ]

    def get_default_permissions(self):
        return {
            "view_photos": True,
            "view_schedule": True,
            "view_documents": True,
            "make_payments": True,
            "approve_selections": True,
            "send_messages": True,
        }

    def save(self, *args, **kwargs):
        if not self.permissions:
            self.permissions = self.get_default_permissions()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contact} — {self.project} portal"


class Selection(TenantModel):
    """
    A material/finish/product decision that the client needs to make.

    Examples: "Master Bath Vanity", "Kitchen Countertop", "Front Door Color"
    """

    class Category(models.TextChoices):
        FLOORING = "FLOORING", "Flooring"
        COUNTERTOPS = "COUNTERTOPS", "Countertops"
        CABINETS = "CABINETS", "Cabinets"
        FIXTURES = "FIXTURES", "Fixtures"
        PAINT = "PAINT", "Paint"
        TILE = "TILE", "Tile"
        HARDWARE = "HARDWARE", "Hardware"
        APPLIANCES = "APPLIANCES", "Appliances"
        LIGHTING = "LIGHTING", "Lighting"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CLIENT_REVIEW = "CLIENT_REVIEW", "Client Review"
        APPROVED = "APPROVED", "Approved"
        ORDERED = "ORDERED", "Ordered"
        INSTALLED = "INSTALLED", "Installed"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="selections",
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    selected_option = models.ForeignKey(
        "SelectionOption",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selected_for_selections",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    due_date = models.DateField(null=True, blank=True)
    assigned_to_client = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "clients_selections"
        verbose_name = "Selection"
        verbose_name_plural = "Selections"
        ordering = ["sort_order", "category"]
        indexes = [
            models.Index(fields=["organization", "project", "status"]),
            models.Index(fields=["organization", "project", "category"]),
            models.Index(fields=["project", "sort_order"]),
        ]

    def __str__(self):
        return f"{self.project} — {self.category}: {self.name}"


class SelectionOption(models.Model):
    """
    Individual choice within a Selection (e.g., "Quartz - Calacatta Gold").

    Not a TenantModel — inherits org via Selection → Project → Organization.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    selection = models.ForeignKey(
        Selection,
        on_delete=models.CASCADE,
        related_name="options",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    price_difference = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Price delta vs. standard/base option (can be negative)",
    )
    lead_time_days = models.IntegerField(null=True, blank=True)
    supplier = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="selections/%Y/%m/", blank=True, null=True)
    spec_sheet_url = models.URLField(blank=True)
    is_recommended = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "clients_selection_options"
        verbose_name = "Selection Option"
        verbose_name_plural = "Selection Options"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["selection", "sort_order"]),
        ]

    def __str__(self):
        return f"{self.selection.name} — {self.name}"


class ClientApproval(TenantModel):
    """
    Formal approval request sent to a client contact.

    Examples: change orders, draw requests, design modifications, schedule changes.
    Supports an optional e-signature (JSONField).
    """

    class ApprovalType(models.TextChoices):
        CHANGE_ORDER = "CHANGE_ORDER", "Change Order"
        SELECTION = "SELECTION", "Selection Approval"
        DRAW_REQUEST = "DRAW_REQUEST", "Draw Request"
        DESIGN_MODIFICATION = "DESIGN_MODIFICATION", "Design Modification"
        SCHEDULE_CHANGE = "SCHEDULE_CHANGE", "Schedule Change"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        EXPIRED = "EXPIRED", "Expired"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="client_approvals",
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.CASCADE,
        related_name="client_approvals",
        null=True,
        blank=True,
    )
    approval_type = models.CharField(max_length=30, choices=ApprovalType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Generic pointer to related object (change order, selection, etc.)
    source_type = models.CharField(max_length=100, blank=True)
    source_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    response_notes = models.TextField(blank=True)
    client_signature = models.JSONField(
        null=True,
        blank=True,
        help_text="Signature data: {name, ip, user_agent, signed_at, image_data}",
    )
    reminded_count = models.IntegerField(default=0)
    last_reminded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clients_approvals"
        verbose_name = "Client Approval"
        verbose_name_plural = "Client Approvals"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["organization", "project", "status"]),
            models.Index(fields=["organization", "project", "approval_type"]),
            models.Index(fields=["organization", "status", "expires_at"]),
        ]

    def __str__(self):
        return f"{self.approval_type}: {self.title} ({self.status})"


class ClientMessage(TenantModel):
    """
    In-portal messaging between contractor staff and client contacts.
    """

    class SenderType(models.TextChoices):
        CONTRACTOR = "CONTRACTOR", "Contractor"
        CLIENT = "CLIENT", "Client"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="client_messages",
    )
    sender_type = models.CharField(max_length=12, choices=SenderType.choices)
    # Only one of these will be set depending on sender_type
    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_messages_sent",
    )
    sender_contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portal_messages_sent",
    )
    subject = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of S3 file keys or document IDs",
    )

    class Meta:
        db_table = "clients_messages"
        verbose_name = "Client Message"
        verbose_name_plural = "Client Messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "project", "-created_at"]),
            models.Index(fields=["organization", "project", "is_read"]),
            models.Index(fields=["sender_type"]),
        ]

    def __str__(self):
        return f"[{self.sender_type}] {self.subject or 'No subject'} — {self.project}"


class ClientSatisfactionSurvey(TenantModel):
    """
    NPS / satisfaction survey triggered at project milestones.
    """

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="satisfaction_surveys",
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.CASCADE,
        related_name="satisfaction_surveys",
    )
    milestone = models.CharField(
        max_length=200,
        blank=True,
        help_text="Which milestone triggered this survey (e.g., 'Framing Complete')",
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Overall satisfaction 1–10",
    )
    nps_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Net Promoter Score 0–10 (would you recommend us?)",
    )
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "clients_satisfaction_surveys"
        verbose_name = "Satisfaction Survey"
        verbose_name_plural = "Satisfaction Surveys"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["organization", "project"]),
            models.Index(fields=["organization", "contact"]),
            models.Index(fields=["organization", "-submitted_at"]),
        ]

    def __str__(self):
        return f"Survey: {self.project} — {self.contact} (rating: {self.rating})"


class PortalBranding(TenantModel):
    """
    Per-organization white-label portal customization.
    OneToOne with Organization — one branding config per org.
    """

    logo = models.ImageField(upload_to="branding/%Y/", blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#2563EB", help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, default="#1E40AF", help_text="Hex color code")
    company_name_override = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Override org name shown in portal (optional)",
    )
    welcome_message = models.TextField(
        blank=True,
        default="Welcome to your project portal. Track progress, approve selections, and stay connected.",
    )
    custom_domain = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Custom domain for white-label portal (e.g., portal.yourcompany.com)",
    )

    class Meta:
        db_table = "clients_portal_branding"
        verbose_name = "Portal Branding"
        verbose_name_plural = "Portal Branding"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Portal Branding — {self.organization.name}"
