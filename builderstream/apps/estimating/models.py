"""Estimating & Takeoffs models."""
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.core.models import TenantModel


class CostCode(TenantModel):
    """CSI MasterFormat classification system for cost items."""

    code = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=200)
    division = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(49)]
    )
    category = models.CharField(max_length=100, blank=True)
    is_labor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "estimating_cost_codes"
        verbose_name = "Cost Code"
        verbose_name_plural = "Cost Codes"
        ordering = ["division", "code"]
        indexes = [
            models.Index(fields=["organization", "division"]),
            models.Index(fields=["organization", "code"]),
            models.Index(fields=["organization", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"], name="unique_cost_code_per_org"
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class CostItem(TenantModel):
    """Library of cost items with pricing."""

    cost_code = models.ForeignKey(
        CostCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cost_items",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20)
    cost = models.DecimalField(max_digits=14, decimal_places=2)
    base_price = models.DecimalField(max_digits=14, decimal_places=2)
    client_price = models.DecimalField(max_digits=14, decimal_places=2)
    markup_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    labor_hours = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    is_taxable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "estimating_cost_items"
        verbose_name = "Cost Item"
        verbose_name_plural = "Cost Items"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "cost_code"]),
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["organization", "is_active"]),
        ]

    def __str__(self):
        return self.name


class Assembly(TenantModel):
    """Template groups of cost items."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    total_cost = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "estimating_assemblies"
        verbose_name = "Assembly"
        verbose_name_plural = "Assemblies"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["organization", "is_active"]),
        ]

    def __str__(self):
        return self.name


class AssemblyItem(TenantModel):
    """Line items within an assembly."""

    assembly = models.ForeignKey(
        Assembly, on_delete=models.CASCADE, related_name="assembly_items"
    )
    cost_item = models.ForeignKey(
        CostItem, on_delete=models.PROTECT, related_name="assembly_items"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    sort_order = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "estimating_assembly_items"
        verbose_name = "Assembly Item"
        verbose_name_plural = "Assembly Items"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["assembly", "sort_order"]),
        ]

    @property
    def line_cost(self):
        """Calculate line cost (not stored)."""
        return self.cost_item.cost * self.quantity

    @property
    def line_price(self):
        """Calculate line price (not stored)."""
        return self.cost_item.client_price * self.quantity

    def __str__(self):
        return f"{self.assembly.name} - {self.cost_item.name}"


class Estimate(TenantModel):
    """Top-level estimate for a project or lead."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in_review", "In Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SENT_TO_CLIENT = "sent_to_client", "Sent to Client"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="estimates",
    )
    lead = models.ForeignKey(
        "crm.Lead",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="estimates",
    )
    name = models.CharField(max_length=200)
    estimate_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.DRAFT
    )
    subtotal = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    tax_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    notes = models.TextField(blank=True)
    valid_until = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_estimates",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_estimates",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "estimating_estimates"
        verbose_name = "Estimate"
        verbose_name_plural = "Estimates"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "project"]),
            models.Index(fields=["organization", "lead"]),
            models.Index(fields=["organization", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.estimate_number} - {self.name}"


class EstimateSection(TenantModel):
    """Organize estimate line items by trade/phase."""

    estimate = models.ForeignKey(
        Estimate, on_delete=models.CASCADE, related_name="sections"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    subtotal = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        db_table = "estimating_sections"
        verbose_name = "Estimate Section"
        verbose_name_plural = "Estimate Sections"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["estimate", "sort_order"]),
        ]

    def __str__(self):
        return f"{self.estimate.estimate_number} - {self.name}"


class EstimateLineItem(TenantModel):
    """Individual line items in estimate."""

    section = models.ForeignKey(
        EstimateSection, on_delete=models.CASCADE, related_name="line_items"
    )
    cost_item = models.ForeignKey(
        CostItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estimate_line_items",
    )
    assembly = models.ForeignKey(
        Assembly,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estimate_line_items",
    )
    description = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    unit = models.CharField(max_length=20)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    is_taxable = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "estimating_line_items"
        verbose_name = "Estimate Line Item"
        verbose_name_plural = "Estimate Line Items"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["section", "sort_order"]),
            models.Index(fields=["cost_item"]),
            models.Index(fields=["assembly"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(cost_item__isnull=False, assembly__isnull=True)
                    | models.Q(cost_item__isnull=True, assembly__isnull=False)
                ),
                name="estimating_line_item_either_cost_or_assembly",
            ),
        ]

    def __str__(self):
        item_name = (
            self.description
            or (self.cost_item.name if self.cost_item else None)
            or (self.assembly.name if self.assembly else "Line Item")
        )
        return f"{self.section.estimate.estimate_number} - {item_name}"


class Proposal(TenantModel):
    """Client-facing proposal document generated from estimate."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        VIEWED = "viewed", "Viewed"
        SIGNED = "signed", "Signed"
        EXPIRED = "expired", "Expired"
        REJECTED = "rejected", "Rejected"

    estimate = models.ForeignKey(
        Estimate, on_delete=models.CASCADE, related_name="proposals"
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposals",
    )
    lead = models.ForeignKey(
        "crm.Lead",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposals",
    )
    client = models.ForeignKey(
        "crm.Contact", on_delete=models.PROTECT, related_name="proposals"
    )
    proposal_number = models.CharField(max_length=50, unique=True, db_index=True)
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    template = models.ForeignKey(
        "ProposalTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposals",
    )
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.DRAFT
    )
    pdf_file = models.FileField(upload_to="proposals/%Y/%m/", blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to_email = models.EmailField(blank=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by_name = models.CharField(max_length=200, blank=True)
    signature_image = models.ImageField(upload_to="signatures/%Y/%m/", blank=True)
    signature_ip = models.GenericIPAddressField(null=True, blank=True)
    signature_user_agent = models.TextField(blank=True)
    is_signed = models.BooleanField(default=False)
    valid_until = models.DateField(null=True, blank=True)
    terms_and_conditions = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "estimating_proposals"
        verbose_name = "Proposal"
        verbose_name_plural = "Proposals"
        ordering = ["-sent_at", "-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "client"]),
            models.Index(fields=["public_token"]),
            models.Index(fields=["organization", "-sent_at"]),
            models.Index(fields=["organization", "is_signed"]),
        ]

    def __str__(self):
        return f"{self.proposal_number} - {self.client.first_name} {self.client.last_name}"


class ProposalTemplate(TenantModel):
    """Customizable PDF templates for proposals."""

    name = models.CharField(max_length=200)
    header_text = models.TextField(blank=True)
    footer_text = models.TextField(blank=True)
    terms_and_conditions = models.TextField()
    signature_instructions = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "estimating_proposal_templates"
        verbose_name = "Proposal Template"
        verbose_name_plural = "Proposal Templates"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "is_default"]),
        ]

    def __str__(self):
        return self.name
