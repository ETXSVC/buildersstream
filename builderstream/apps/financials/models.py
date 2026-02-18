"""Financial Management Suite — job costing, invoicing, change orders, purchase orders."""
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.models import TenantModel, TimeStampedModel


class CostCode(TenantModel):
    """CSI MasterFormat-style cost codes for job costing."""

    class Division(models.IntegerChoices):
        GENERAL_CONDITIONS = 1, "01 - General Conditions"
        EXISTING_CONDITIONS = 2, "02 - Existing Conditions"
        CONCRETE = 3, "03 - Concrete"
        MASONRY = 4, "04 - Masonry"
        METALS = 5, "05 - Metals"
        WOOD_PLASTICS = 6, "06 - Wood, Plastics & Composites"
        THERMAL_MOISTURE = 7, "07 - Thermal & Moisture Protection"
        OPENINGS = 8, "08 - Openings"
        FINISHES = 9, "09 - Finishes"
        SPECIALTIES = 10, "10 - Specialties"
        EQUIPMENT = 11, "11 - Equipment"
        FURNISHINGS = 12, "12 - Furnishings"
        SPECIAL_CONSTRUCTION = 13, "13 - Special Construction"
        CONVEYING = 14, "14 - Conveying Equipment"
        UTILITIES = 22, "22 - Plumbing"
        HVAC = 23, "23 - HVAC"
        ELECTRICAL = 26, "26 - Electrical"
        EARTHWORK = 31, "31 - Earthwork"
        EXTERIOR_IMPROVEMENTS = 32, "32 - Exterior Improvements"
        UTILITIES_GENERAL = 33, "33 - Utilities"

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    division = models.IntegerField(choices=Division.choices, default=Division.GENERAL_CONDITIONS)
    category = models.CharField(max_length=100, blank=True)
    is_labor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [["organization", "code"]]
        indexes = [
            models.Index(fields=["organization", "division"], name="fin_costcode_org_div_idx"),
            models.Index(fields=["organization", "is_active"], name="fin_costcode_org_active_idx"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Budget(TenantModel):
    """Line-item budget for a project, organized by cost code."""

    class BudgetType(models.TextChoices):
        ORIGINAL = "original", "Original"
        REVISED = "revised", "Revised"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="budget_lines",
    )
    cost_code = models.ForeignKey(
        CostCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="budget_lines",
    )
    description = models.CharField(max_length=200)
    budget_type = models.CharField(max_length=20, choices=BudgetType.choices, default=BudgetType.ORIGINAL)
    budgeted_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    committed_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    # Auto-calculated
    variance_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    variance_percent = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.00"))
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "project"], name="fin_budget_org_proj_idx"),
            models.Index(fields=["organization", "cost_code"], name="fin_budget_org_code_idx"),
        ]

    def __str__(self):
        return f"Budget: {self.project} / {self.description}"

    def calculate_variance(self):
        """Recalculate variance fields from current actual_amount."""
        self.variance_amount = self.budgeted_amount - self.actual_amount
        if self.budgeted_amount:
            self.variance_percent = (self.variance_amount / self.budgeted_amount) * Decimal("100")
        else:
            self.variance_percent = Decimal("0.00")

    def save(self, *args, **kwargs):
        self.calculate_variance()
        super().save(*args, **kwargs)


class Expense(TenantModel):
    """An individual expense (cost) on a project."""

    class ExpenseType(models.TextChoices):
        MATERIAL = "material", "Material"
        LABOR = "labor", "Labor"
        SUBCONTRACTOR = "subcontractor", "Subcontractor"
        EQUIPMENT = "equipment", "Equipment"
        OVERHEAD = "overhead", "Overhead"
        OTHER = "other", "Other"

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="financial_expenses",
    )
    cost_code = models.ForeignKey(
        CostCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    budget_line = models.ForeignKey(
        Budget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    expense_type = models.CharField(max_length=20, choices=ExpenseType.choices, default=ExpenseType.OTHER)
    vendor_name = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    expense_date = models.DateField()
    # Receipt
    receipt_key = models.CharField(max_length=500, blank=True)  # S3 file key
    receipt_url = models.URLField(max_length=500, blank=True)   # presigned URL (transient)
    # Approval
    approval_status = models.CharField(
        max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_expenses",
    )
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "project"], name="fin_expense_org_proj_idx"),
            models.Index(fields=["organization", "expense_date"], name="fin_expense_org_date_idx"),
            models.Index(fields=["organization", "approval_status"], name="fin_expense_org_status_idx"),
        ]

    def __str__(self):
        return f"{self.description} — ${self.amount}"


class Invoice(TenantModel):
    """Client invoice for project work completed."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        VIEWED = "viewed", "Viewed"
        PARTIAL = "partial", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        VOID = "void", "Void"

    class InvoiceType(models.TextChoices):
        STANDARD = "standard", "Standard Invoice"
        PROGRESS = "progress", "Progress Billing (AIA G702)"
        FINAL = "final", "Final Invoice"
        RETAINAGE = "retainage", "Retainage Release"
        DEPOSIT = "deposit", "Deposit Request"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    client = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    invoice_number = models.CharField(max_length=50)
    invoice_type = models.CharField(max_length=20, choices=InvoiceType.choices, default=InvoiceType.STANDARD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # Public access token (for client-facing invoice view)
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    # Amounts
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    retainage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    retainage_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    balance_due = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    # AIA Progress billing fields
    scheduled_value = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    work_completed_previous = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    work_completed_this_period = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    # Dates
    issue_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to_email = models.EmailField(blank=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    # Stripe integration
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    # Content
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
    )

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status"], name="fin_invoice_org_status_idx"),
            models.Index(fields=["organization", "project"], name="fin_invoice_org_proj_idx"),
            models.Index(fields=["organization", "due_date"], name="fin_invoice_org_due_idx"),
            models.Index(fields=["public_token"], name="fin_invoice_token_idx"),
        ]

    def __str__(self):
        return f"Invoice #{self.invoice_number} — {self.project}"

    def recalculate_totals(self):
        """Recalculate totals from line items."""
        line_totals = self.line_items.aggregate(total=models.Sum("line_total"))["total"] or Decimal("0.00")
        self.subtotal = line_totals
        self.tax_amount = self.subtotal * (self.tax_rate / Decimal("100"))
        self.retainage_amount = self.subtotal * (self.retainage_percent / Decimal("100"))
        self.total = self.subtotal + self.tax_amount - self.retainage_amount
        self.balance_due = self.total - self.amount_paid


class InvoiceLineItem(TimeStampedModel):
    """Line item on an invoice — NOT a TenantModel (org via Invoice FK)."""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("1.0000"))
    unit = models.CharField(max_length=20, blank=True)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    cost_code = models.ForeignKey(
        CostCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_lines",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.description} — ${self.line_total}"

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(TenantModel):
    """Payment received against an invoice."""

    class PaymentMethod(models.TextChoices):
        CHECK = "check", "Check"
        ACH = "ach", "ACH / Bank Transfer"
        CREDIT_CARD = "credit_card", "Credit Card"
        WIRE = "wire", "Wire Transfer"
        CASH = "cash", "Cash"
        STRIPE = "stripe", "Stripe"
        OTHER = "other", "Other"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CHECK)
    reference_number = models.CharField(max_length=100, blank=True)  # Check #, transaction ID, etc.
    stripe_charge_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_payments",
    )

    class Meta:
        indexes = [
            models.Index(fields=["organization", "invoice"], name="fin_payment_org_inv_idx"),
            models.Index(fields=["organization", "payment_date"], name="fin_payment_org_date_idx"),
        ]

    def __str__(self):
        return f"Payment ${self.amount} on {self.payment_date}"


class ChangeOrder(TenantModel):
    """Project change order for scope changes impacting cost and/or schedule."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted to Client"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        VOID = "void", "Void"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="change_orders",
    )
    number = models.PositiveIntegerField()  # Auto-incremented per project
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # Financial impact
    cost_impact = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    # Schedule impact
    schedule_impact_days = models.IntegerField(default=0)
    # Client approval
    client = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_orders",
    )
    submitted_date = models.DateField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    rejected_date = models.DateField(null=True, blank=True)
    approved_by_name = models.CharField(max_length=200, blank=True)  # Client signatory name
    # Internal
    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_change_orders",
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = [["project", "number"]]
        indexes = [
            models.Index(fields=["organization", "project"], name="fin_co_org_proj_idx"),
            models.Index(fields=["organization", "status"], name="fin_co_org_status_idx"),
        ]

    def __str__(self):
        return f"CO #{self.number:03d} — {self.title}"


class ChangeOrderLineItem(TimeStampedModel):
    """Line item on a change order — NOT a TenantModel (org via ChangeOrder FK)."""

    change_order = models.ForeignKey(ChangeOrder, on_delete=models.CASCADE, related_name="line_items")
    cost_code = models.ForeignKey(
        CostCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="co_lines",
    )
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("1.0000"))
    unit = models.CharField(max_length=20, blank=True)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.description} — ${self.line_total}"

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class PurchaseOrder(TenantModel):
    """Purchase order issued to a vendor/subcontractor."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent to Vendor"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        PARTIAL = "partial", "Partially Received"
        RECEIVED = "received", "Fully Received"
        CLOSED = "closed", "Closed"
        CANCELED = "canceled", "Canceled"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="purchase_orders",
    )
    po_number = models.CharField(max_length=50)
    vendor_name = models.CharField(max_length=200)
    vendor_email = models.EmailField(blank=True)
    vendor_phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # Amounts (auto-calculated from line items)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    # Dates
    issue_date = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    delivery_location = models.CharField(max_length=200, blank=True)
    # Content
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_purchase_orders",
    )

    class Meta:
        indexes = [
            models.Index(fields=["organization", "project"], name="fin_po_org_proj_idx"),
            models.Index(fields=["organization", "status"], name="fin_po_org_status_idx"),
            models.Index(fields=["organization", "vendor_name"], name="fin_po_org_vendor_idx"),
        ]

    def __str__(self):
        return f"PO #{self.po_number} — {self.vendor_name}"

    def recalculate_totals(self):
        """Recalculate PO totals from line items."""
        agg = self.line_items.aggregate(total=models.Sum("line_total"))
        self.subtotal = agg["total"] or Decimal("0.00")
        self.total = self.subtotal + self.tax_amount


class PurchaseOrderLineItem(TimeStampedModel):
    """Line item on a PO with receiving tracking — NOT a TenantModel."""

    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="line_items")
    cost_code = models.ForeignKey(
        CostCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="po_lines",
    )
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    unit = models.CharField(max_length=20, blank=True)
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    received_quantity = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("0.0000"))
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.description} — {self.quantity} {self.unit}"

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
