"""Billing views — subscription management, portal, invoices, plan comparison."""
import logging

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOrganizationOwner, role_required

from .models import Invoice
from .plans import PLAN_CONFIG
from .serializers import (
    CreateSubscriptionSerializer,
    InvoiceSerializer,
    PlanDetailSerializer,
    SubscriptionStatusSerializer,
    UpdateSubscriptionSerializer,
)
from .services import ModuleGateService, StripeService

logger = logging.getLogger(__name__)


class SubscriptionView(APIView):
    """Manage the organization's Stripe subscription.

    GET    — current plan, status, usage stats
    POST   — create a new subscription
    PATCH  — change plan (upgrade/downgrade)
    DELETE — cancel subscription
    """

    permission_classes = [IsAuthenticated, role_required("admin")]

    def get(self, request):
        org = request.organization
        plan_key = org.subscription_plan.upper()
        plan_cfg = PLAN_CONFIG.get(plan_key, {})
        limits = ModuleGateService.get_plan_limits(org)

        active_modules = list(
            org.active_modules.filter(is_active=True).values_list("module_key", flat=True)
        )

        data = {
            "plan_key": plan_key,
            "plan_name": plan_cfg.get("name", "Unknown"),
            "status": org.subscription_status,
            "trial_ends_at": org.trial_ends_at,
            "users_used": org.member_count,
            "max_users": limits["max_users"],
            "active_modules": active_modules,
            "available_modules": limits["modules"],
            "stripe_subscription_id": org.stripe_subscription_id or "",
        }
        serializer = SubscriptionStatusSerializer(data)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        org = request.organization
        try:
            StripeService.create_subscription(
                org,
                plan_key=serializer.validated_data["plan_key"],
                billing_interval=serializer.validated_data["billing_interval"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Failed to create subscription for %s", org)
            return Response(
                {"detail": "Failed to create subscription. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"detail": "Subscription created."}, status=status.HTTP_201_CREATED)

    def patch(self, request):
        serializer = UpdateSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        org = request.organization
        try:
            StripeService.update_subscription(
                org,
                new_plan_key=serializer.validated_data["new_plan_key"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Failed to update subscription for %s", org)
            return Response(
                {"detail": "Failed to update subscription. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"detail": "Subscription updated."})

    def delete(self, request):
        org = request.organization
        try:
            StripeService.cancel_subscription(org, at_period_end=True)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Failed to cancel subscription for %s", org)
            return Response(
                {"detail": "Failed to cancel subscription. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"detail": "Subscription will be canceled at end of billing period."})


class BillingPortalView(APIView):
    """Create a Stripe Customer Portal session for self-service billing."""

    permission_classes = [IsAuthenticated, IsOrganizationOwner]

    def post(self, request):
        org = request.organization
        try:
            url = StripeService.create_billing_portal_session(org)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("Failed to create billing portal session for %s", org)
            return Response(
                {"detail": "Failed to open billing portal."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response({"url": url})


class InvoiceListView(ListAPIView):
    """List invoices for the current organization."""

    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, role_required("accountant")]

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        if org is None:
            return Invoice.objects.none()
        return Invoice.objects.filter(organization=org)


class PlanComparisonView(APIView):
    """Public endpoint returning all plans with pricing and features.

    Used by the frontend pricing page — no authentication required.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        plans = []
        for key, cfg in PLAN_CONFIG.items():
            plans.append(
                {
                    "key": key,
                    "name": cfg["name"],
                    "max_users": cfg["max_users"],
                    "price_monthly_per_user": cfg.get("price_monthly_per_user", 0),
                    "price_annual_per_user": cfg.get("price_annual_per_user", 0),
                    "modules": cfg["modules"],
                    "trial_days": cfg.get("trial_days"),
                }
            )
        serializer = PlanDetailSerializer(plans, many=True)
        return Response(serializer.data)
