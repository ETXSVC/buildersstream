"""CRM models: contacts, companies, pipeline stages, leads, interactions, automation, email templates."""
from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class Contact(TenantModel):
    """Contact in the CRM system - leads, clients, subcontractors, vendors, etc."""

    class ContactType(models.TextChoices):
        LEAD = "lead", "Lead"
        CLIENT = "client", "Client"
        SUBCONTRACTOR = "subcontractor", "Subcontractor"
        VENDOR = "vendor", "Vendor"
        ARCHITECT = "architect", "Architect"
        OTHER = "other", "Other"

    class Source(models.TextChoices):
        WEBSITE_FORM = "website_form", "Website Form"
        PHONE = "phone", "Phone Call"
        EMAIL = "email", "Email"
        REFERRAL = "referral", "Referral"
        HOME_ADVISOR = "home_advisor", "HomeAdvisor"
        ANGI = "angi", "Angi (Angie's List)"
        HOUZZ = "houzz", "Houzz"
        HOME_SHOW = "home_show", "Home Show"
        SOCIAL_MEDIA = "social_media", "Social Media"
        WALK_IN = "walk_in", "Walk-In"
        OTHER = "other", "Other"

    # Core fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)

    # Company relationship (both FK and CharField for backward compatibility)
    company = models.ForeignKey(
        "Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
    )
    company_name = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)

    # Address fields
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    # Classification
    contact_type = models.CharField(
        max_length=20,
        choices=ContactType.choices,
        default=ContactType.LEAD,
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        blank=True,
    )

    # Referral tracking
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
    )

    # Lead scoring and metadata
    lead_score = models.IntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)

    # Status
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "contact_type"]),
            models.Index(fields=["organization", "-lead_score"]),
            models.Index(fields=["organization", "-created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Company(TenantModel):
    """Company/organization for contacts - clients, subcontractors, vendors, suppliers."""

    class CompanyType(models.TextChoices):
        CLIENT_COMPANY = "client_company", "Client Company"
        SUBCONTRACTOR = "subcontractor", "Subcontractor"
        VENDOR = "vendor", "Vendor"
        SUPPLIER = "supplier", "Supplier"
        ARCHITECT_FIRM = "architect_firm", "Architect Firm"

    # Core fields
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Classification
    company_type = models.CharField(
        max_length=20,
        choices=CompanyType.choices,
        default=CompanyType.CLIENT_COMPANY,
    )

    # Compliance and performance
    insurance_expiry = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    performance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Rating from 1.00 to 5.00",
    )

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PipelineStage(TenantModel):
    """Configurable sales pipeline stages."""

    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color code")

    # Stage type flags
    is_won_stage = models.BooleanField(default=False)
    is_lost_stage = models.BooleanField(default=False)

    # Automation config
    auto_actions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Automatic actions triggered when lead enters this stage",
    )

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class Lead(TenantModel):
    """Sales lead/opportunity in the pipeline."""

    class ProjectType(models.TextChoices):
        """Mirror of Project.ProjectType for consistency."""
        CUSTOM_HOME = "custom_home", "Custom Home"
        RESIDENTIAL_REMODEL = "residential_remodel", "Residential Remodel"
        KITCHEN_BATH = "kitchen_bath", "Kitchen & Bath"
        ADDITION = "addition", "Addition"
        COMMERCIAL = "commercial", "Commercial"
        TENANT_IMPROVEMENT = "tenant_improvement", "Tenant Improvement"
        ROOFING = "roofing", "Roofing"
        SIDING = "siding", "Siding"
        OTHER = "other", "Other"

    class Urgency(models.TextChoices):
        HOT = "hot", "Hot - Immediate"
        WARM = "warm", "Warm - 1-3 Months"
        COLD = "cold", "Cold - 3+ Months"

    # Core relationships
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="leads",
    )
    pipeline_stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.PROTECT,
        related_name="leads",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
    )

    # Project details
    project_type = models.CharField(
        max_length=30,
        choices=ProjectType.choices,
        blank=True,
    )
    estimated_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    estimated_start = models.DateField(null=True, blank=True)

    # Lead classification
    urgency = models.CharField(
        max_length=10,
        choices=Urgency.choices,
        default=Urgency.WARM,
    )

    # Description
    description = models.TextField(blank=True)

    # Loss tracking (for lost leads)
    lost_reason = models.CharField(max_length=255, blank=True)
    lost_to_competitor = models.CharField(max_length=255, blank=True)

    # Conversion tracking
    converted_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_lead",
    )

    # Activity tracking
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "pipeline_stage"]),
            models.Index(fields=["organization", "assigned_to"]),
            models.Index(fields=["organization", "-last_contacted_at"]),
            models.Index(fields=["organization", "next_follow_up"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.contact.first_name} {self.contact.last_name} - {self.project_type or 'Lead'}"


class Interaction(TenantModel):
    """Communication log for contacts and leads."""

    class InteractionType(models.TextChoices):
        EMAIL = "email", "Email"
        PHONE_CALL = "phone_call", "Phone Call"
        SMS = "sms", "SMS/Text Message"
        SITE_VISIT = "site_visit", "Site Visit"
        MEETING = "meeting", "Meeting"
        NOTE = "note", "Note"

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    # Relationships
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name="interactions",
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="interactions",
    )
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="logged_interactions",
    )

    # Interaction details
    interaction_type = models.CharField(
        max_length=20,
        choices=InteractionType.choices,
    )
    direction = models.CharField(
        max_length=10,
        choices=Direction.choices,
        default=Direction.OUTBOUND,
    )

    # Content
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()

    # Timing
    occurred_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["organization", "contact", "-occurred_at"]),
            models.Index(fields=["organization", "lead", "-occurred_at"]),
        ]
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.interaction_type} with {self.contact} on {self.occurred_at.date()}"


class AutomationRule(TenantModel):
    """Automation rules for CRM workflows."""

    class TriggerType(models.TextChoices):
        STAGE_CHANGE = "stage_change", "Stage Change"
        TIME_DELAY = "time_delay", "Time Delay (Inactivity)"
        LEAD_SCORE_CHANGE = "lead_score_change", "Lead Score Change"
        NO_ACTIVITY = "no_activity", "No Activity Period"

    class ActionType(models.TextChoices):
        SEND_EMAIL = "send_email", "Send Email"
        SEND_SMS = "send_sms", "Send SMS"
        CREATE_TASK = "create_task", "Create Task"
        ASSIGN_LEAD = "assign_lead", "Assign Lead"
        CHANGE_STAGE = "change_stage", "Change Stage"
        NOTIFY_USER = "notify_user", "Notify User"

    # Rule definition
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    # Trigger configuration
    trigger_type = models.CharField(
        max_length=20,
        choices=TriggerType.choices,
    )
    trigger_config = models.JSONField(
        default=dict,
        help_text='Example: {"stage_id": "uuid"} or {"days_inactive": 7}',
    )

    # Action configuration
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
    )
    action_config = models.JSONField(
        default=dict,
        help_text='Example: {"template_id": "uuid", "assign_to_id": "uuid"}',
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmailTemplate(TenantModel):
    """Email templates for CRM communications."""

    class TemplateType(models.TextChoices):
        FOLLOW_UP = "follow_up", "Follow-Up"
        THANK_YOU = "thank_you", "Thank You"
        ESTIMATE_REMINDER = "estimate_reminder", "Estimate Reminder"
        REVIEW_REQUEST = "review_request", "Review Request"
        MARKETING = "marketing", "Marketing"

    # Template definition
    name = models.CharField(max_length=200)
    template_type = models.CharField(
        max_length=20,
        choices=TemplateType.choices,
    )

    # Email content
    subject = models.CharField(max_length=255)
    body = models.TextField(
        help_text="Supports variables: {{first_name}}, {{last_name}}, {{project_type}}, {{company_name}}, {{estimated_value}}",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
