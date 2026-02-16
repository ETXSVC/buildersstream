"""Multi-tenant organization models."""
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel


class Organization(TimeStampedModel):
    """Represents a company/organization in the multi-tenant system."""

    class IndustryType(models.TextChoices):
        RESIDENTIAL_REMODEL = "residential_remodel", "Residential Remodel"
        CUSTOM_HOME = "custom_home", "Custom Home Builder"
        COMMERCIAL_GC = "commercial_gc", "Commercial General Contractor"
        SPECIALTY_TRADE = "specialty_trade", "Specialty Trade"
        ROOFING_EXTERIOR = "roofing_exterior", "Roofing & Exterior"
        ENTERPRISE = "enterprise", "Enterprise"

    class SubscriptionPlan(models.TextChoices):
        STARTER = "starter", "Starter"
        PROFESSIONAL = "professional", "Professional"
        ENTERPRISE = "enterprise", "Enterprise"
        TRIAL = "trial", "Trial"

    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELED = "canceled", "Canceled"
        TRIALING = "trialing", "Trialing"

    # Identity
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
    )
    logo = models.ImageField(upload_to="org_logos/", blank=True, null=True)

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="US")

    # Business
    industry_type = models.CharField(
        max_length=30,
        choices=IndustryType.choices,
        blank=True,
    )

    # Stripe / Billing
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.TRIAL,
    )
    subscription_status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIALING,
    )
    trial_ends_at = models.DateTimeField(blank=True, null=True)
    max_users = models.IntegerField(default=5)

    # Status
    is_active = models.BooleanField(default=True)

    # Organization-level settings (fiscal year start, timezone, date format, etc.)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.filter(is_active=True).count()


class OrganizationMembership(TimeStampedModel):
    """Through table linking Users to Organizations with roles."""

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        PROJECT_MANAGER = "project_manager", "Project Manager"
        ESTIMATOR = "estimator", "Estimator"
        FIELD_WORKER = "field_worker", "Field Worker"
        ACCOUNTANT = "accountant", "Accountant"
        READ_ONLY = "read_only", "Read Only"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READ_ONLY,
    )
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations_sent",
    )
    invited_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ["user", "organization"]

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.get_role_display()})"


class ActiveModule(TimeStampedModel):
    """Tracks which modules an organization has enabled."""

    class ModuleKey(models.TextChoices):
        PROJECT_CENTER = "project_center", "Project Command Center"
        CRM = "crm", "CRM & Lead Management"
        ESTIMATING = "estimating", "Estimating & Takeoffs"
        SCHEDULING = "scheduling", "Scheduling & Resources"
        FINANCIALS = "financials", "Financial Management"
        CLIENT_PORTAL = "client_portal", "Client Portal"
        DOCUMENTS = "documents", "Document Management"
        FIELD_OPS = "field_ops", "Field Operations"
        QUALITY_SAFETY = "quality_safety", "Quality & Safety"
        PAYROLL = "payroll", "Payroll"
        SERVICE_WARRANTY = "service_warranty", "Service & Warranty"
        ANALYTICS = "analytics", "Analytics & Reporting"

    # Modules that are always active and cannot be deactivated
    ALWAYS_ACTIVE = {ModuleKey.PROJECT_CENTER, ModuleKey.ANALYTICS}

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="active_modules",
    )
    module_key = models.CharField(max_length=30, choices=ModuleKey.choices)
    is_active = models.BooleanField(default=True)
    activated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["organization", "module_key"]

    def __str__(self):
        return f"{self.organization} - {self.get_module_key_display()}"

    def save(self, *args, **kwargs):
        # Prevent deactivating always-active modules
        if self.module_key in self.ALWAYS_ACTIVE:
            self.is_active = True
        super().save(*args, **kwargs)
