"""Financial Management Suite serializers."""
from rest_framework import serializers

from .models import (
    Budget,
    ChangeOrder,
    ChangeOrderLineItem,
    CostCode,
    Expense,
    Invoice,
    InvoiceLineItem,
    Payment,
    PurchaseOrder,
    PurchaseOrderLineItem,
)


# ───────────────────────────── CostCode ──────────────────────────────────── #

class CostCodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCode
        fields = ["id", "code", "name", "division", "category", "is_labor", "is_active"]
        read_only_fields = ["id"]


class CostCodeSerializer(serializers.ModelSerializer):
    division_display = serializers.CharField(source="get_division_display", read_only=True)

    class Meta:
        model = CostCode
        fields = [
            "id", "code", "name", "division", "division_display",
            "category", "is_labor", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# ───────────────────────────── Budget ────────────────────────────────────── #

class BudgetListSerializer(serializers.ModelSerializer):
    cost_code_name = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id", "project", "cost_code", "cost_code_name", "description",
            "budget_type", "budgeted_amount", "committed_amount", "actual_amount",
            "variance_amount", "variance_percent",
        ]
        read_only_fields = ["id", "variance_amount", "variance_percent"]

    def get_cost_code_name(self, obj):
        return str(obj.cost_code) if obj.cost_code else None


class BudgetSerializer(serializers.ModelSerializer):
    cost_code_name = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            "id", "project", "cost_code", "cost_code_name", "description",
            "budget_type", "budgeted_amount", "committed_amount", "actual_amount",
            "variance_amount", "variance_percent", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "variance_amount", "variance_percent", "created_at", "updated_at"]

    def get_cost_code_name(self, obj):
        return str(obj.cost_code) if obj.cost_code else None


# ───────────────────────────── Expense ───────────────────────────────────── #

class ExpenseListSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id", "project", "cost_code", "expense_type", "vendor_name",
            "description", "amount", "expense_date", "approval_status",
            "submitted_by", "submitted_by_name",
        ]
        read_only_fields = ["id"]

    def get_submitted_by_name(self, obj):
        return obj.submitted_by.get_full_name() if obj.submitted_by else None


class ExpenseSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id", "project", "cost_code", "budget_line",
            "expense_type", "vendor_name", "description",
            "amount", "tax_amount", "expense_date",
            "receipt_key", "receipt_url",
            "approval_status", "approved_by", "approved_by_name", "approved_at",
            "submitted_by", "submitted_by_name",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "approved_by", "approved_at", "created_at", "updated_at",
        ]

    def get_submitted_by_name(self, obj):
        return obj.submitted_by.get_full_name() if obj.submitted_by else None

    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None


class ExpenseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "project", "cost_code", "budget_line",
            "expense_type", "vendor_name", "description",
            "amount", "tax_amount", "expense_date",
            "receipt_key", "notes",
        ]


# ───────────────────────────── InvoiceLineItem ────────────────────────────── #

class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = [
            "id", "invoice", "cost_code", "description",
            "quantity", "unit", "unit_price", "line_total", "sort_order",
        ]
        read_only_fields = ["id", "line_total"]


class InvoiceLineItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = ["invoice", "cost_code", "description", "quantity", "unit", "unit_price", "sort_order"]


# ───────────────────────────── Invoice ───────────────────────────────────── #

class InvoiceListSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id", "invoice_number", "invoice_type", "status",
            "project", "project_name", "client", "client_name",
            "subtotal", "total", "balance_due",
            "issue_date", "due_date", "paid_date",
        ]
        read_only_fields = ["id"]

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None

    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None


class InvoiceSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id", "invoice_number", "invoice_type", "status", "public_token",
            "project", "project_name", "client", "client_name",
            "subtotal", "tax_rate", "tax_amount", "retainage_percent", "retainage_amount",
            "total", "amount_paid", "balance_due",
            "scheduled_value", "work_completed_previous", "work_completed_this_period",
            "issue_date", "due_date", "paid_date",
            "sent_at", "sent_to_email", "viewed_at", "view_count",
            "stripe_invoice_id", "stripe_payment_intent_id",
            "notes", "terms", "created_by",
            "line_items", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "invoice_number", "public_token",
            "subtotal", "tax_amount", "retainage_amount", "total", "balance_due",
            "amount_paid", "sent_at", "viewed_at", "view_count",
            "stripe_invoice_id", "stripe_payment_intent_id",
            "created_by", "created_at", "updated_at",
        ]

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None

    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None


class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "project", "client", "invoice_type",
            "tax_rate", "retainage_percent",
            "issue_date", "due_date",
            "scheduled_value", "work_completed_previous", "work_completed_this_period",
            "notes", "terms",
        ]


# ───────────────────────────── Payment ───────────────────────────────────── #

class PaymentSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id", "invoice", "project", "amount",
            "payment_date", "payment_method", "reference_number",
            "stripe_charge_id", "notes",
            "recorded_by", "recorded_by_name", "created_at",
        ]
        read_only_fields = ["id", "stripe_charge_id", "recorded_by", "created_at"]

    def get_recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else None


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["invoice", "project", "amount", "payment_date", "payment_method", "reference_number", "notes"]


# ───────────────────────────── ChangeOrderLineItem ────────────────────────── #

class ChangeOrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeOrderLineItem
        fields = [
            "id", "change_order", "cost_code", "description",
            "quantity", "unit", "unit_cost", "line_total", "sort_order",
        ]
        read_only_fields = ["id", "line_total"]


class ChangeOrderLineItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeOrderLineItem
        fields = ["change_order", "cost_code", "description", "quantity", "unit", "unit_cost", "sort_order"]


# ───────────────────────────── ChangeOrder ───────────────────────────────── #

class ChangeOrderListSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = ChangeOrder
        fields = [
            "id", "number", "title", "status", "project", "project_name",
            "cost_impact", "schedule_impact_days", "submitted_date", "approved_date",
        ]
        read_only_fields = ["id", "number"]

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None


class ChangeOrderSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    client_name = serializers.SerializerMethodField()
    line_items = ChangeOrderLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = ChangeOrder
        fields = [
            "id", "number", "title", "description", "status",
            "project", "project_name", "client", "client_name",
            "cost_impact", "schedule_impact_days",
            "submitted_date", "approved_date", "rejected_date", "approved_by_name",
            "reason", "notes", "created_by",
            "line_items", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "number", "cost_impact",
            "submitted_date", "approved_date", "rejected_date",
            "created_by", "created_at", "updated_at",
        ]

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None

    def get_client_name(self, obj):
        return str(obj.client) if obj.client else None


class ChangeOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeOrder
        fields = ["project", "client", "title", "description", "schedule_impact_days", "reason", "notes"]


# ───────────────────────────── PurchaseOrderLineItem ──────────────────────── #

class PurchaseOrderLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLineItem
        fields = [
            "id", "purchase_order", "cost_code", "description",
            "quantity", "unit", "unit_price", "line_total",
            "received_quantity", "sort_order",
        ]
        read_only_fields = ["id", "line_total"]


class PurchaseOrderLineItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLineItem
        fields = ["purchase_order", "cost_code", "description", "quantity", "unit", "unit_price", "sort_order"]


# ───────────────────────────── PurchaseOrder ──────────────────────────────── #

class PurchaseOrderListSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrder
        fields = [
            "id", "po_number", "vendor_name", "status",
            "project", "project_name", "subtotal", "total",
            "issue_date", "expected_delivery_date", "actual_delivery_date",
        ]
        read_only_fields = ["id", "po_number"]

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None


class PurchaseOrderSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    line_items = PurchaseOrderLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id", "po_number", "vendor_name", "vendor_email", "vendor_phone",
            "status", "project", "project_name",
            "subtotal", "tax_amount", "total",
            "issue_date", "expected_delivery_date", "actual_delivery_date",
            "delivery_location", "notes", "terms", "created_by",
            "line_items", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "po_number", "subtotal", "total",
            "created_by", "created_at", "updated_at",
        ]

    def get_project_name(self, obj):
        return str(obj.project) if obj.project else None


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = [
            "project", "vendor_name", "vendor_email", "vendor_phone",
            "tax_amount", "issue_date", "expected_delivery_date",
            "delivery_location", "notes", "terms",
        ]
