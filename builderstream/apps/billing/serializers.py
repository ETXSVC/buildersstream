"""Billing serializers."""
from rest_framework import serializers

from .models import Invoice
from .plans import PAID_PLAN_KEYS


class CreateSubscriptionSerializer(serializers.Serializer):
    """Validates input for creating a new subscription."""

    plan_key = serializers.ChoiceField(choices=[(k, k) for k in PAID_PLAN_KEYS])
    billing_interval = serializers.ChoiceField(
        choices=[("monthly", "Monthly"), ("annual", "Annual")],
        default="monthly",
    )


class UpdateSubscriptionSerializer(serializers.Serializer):
    """Validates input for upgrading/downgrading a subscription."""

    new_plan_key = serializers.ChoiceField(choices=[(k, k) for k in PAID_PLAN_KEYS])


class SubscriptionStatusSerializer(serializers.Serializer):
    """Read-only representation of the org's current subscription state."""

    plan_key = serializers.CharField()
    plan_name = serializers.CharField()
    status = serializers.CharField()
    trial_ends_at = serializers.DateTimeField(allow_null=True)
    users_used = serializers.IntegerField()
    max_users = serializers.IntegerField()
    active_modules = serializers.ListField(child=serializers.CharField())
    available_modules = serializers.ListField(child=serializers.CharField())
    stripe_subscription_id = serializers.CharField(allow_null=True, allow_blank=True)


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice records."""

    amount_due_display = serializers.SerializerMethodField()
    amount_paid_display = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "stripe_invoice_id",
            "amount_due",
            "amount_paid",
            "amount_due_display",
            "amount_paid_display",
            "currency",
            "status",
            "period_start",
            "period_end",
            "hosted_invoice_url",
            "pdf_url",
            "created_at",
        ]
        read_only_fields = fields

    def get_amount_due_display(self, obj):
        return f"${obj.amount_due / 100:.2f}"

    def get_amount_paid_display(self, obj):
        return f"${obj.amount_paid / 100:.2f}"


class PlanDetailSerializer(serializers.Serializer):
    """Serializes a single plan from PLAN_CONFIG for the public pricing page."""

    key = serializers.CharField()
    name = serializers.CharField()
    max_users = serializers.IntegerField()
    price_monthly_per_user = serializers.IntegerField(default=0)
    price_annual_per_user = serializers.IntegerField(default=0)
    modules = serializers.ListField(child=serializers.CharField())
    trial_days = serializers.IntegerField(required=False)
