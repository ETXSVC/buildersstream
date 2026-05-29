"""Billing service layer — Stripe operations and module gating."""
import logging
from datetime import datetime, timezone as dt_tz

import stripe
from django.conf import settings
from django.utils import timezone

from apps.tenants.models import ActiveModule, Organization

from .plans import PAID_PLAN_KEYS, PLAN_CONFIG, STRIPE_PRICE_TO_PLAN

logger = logging.getLogger(__name__)


def _configure_stripe():
    """Set the Stripe API key from Django settings."""
    stripe.api_key = settings.STRIPE_SECRET_KEY


# ---------------------------------------------------------------------------
# StripeService
# ---------------------------------------------------------------------------


class StripeService:
    """Encapsulates all Stripe API interactions for subscription billing."""

    # -- Customer management ------------------------------------------------

    @staticmethod
    def create_customer(organization):
        """Create a Stripe Customer for *organization* and persist the ID.

        This is also called from ``apps.tenants.signals`` on org creation,
        but having it here makes it re-usable from views and tasks.
        """
        _configure_stripe()

        if organization.stripe_customer_id:
            return organization.stripe_customer_id

        customer = stripe.Customer.create(
            name=organization.name,
            email=organization.email or organization.owner.email,
            metadata={"organization_id": str(organization.id)},
        )
        Organization.objects.filter(pk=organization.pk).update(
            stripe_customer_id=customer.id,
        )
        organization.stripe_customer_id = customer.id
        logger.info("Created Stripe customer %s for %s", customer.id, organization)
        return customer.id

    # -- Subscription CRUD --------------------------------------------------

    @staticmethod
    def create_subscription(organization, plan_key, billing_interval="monthly"):
        """Create a new Stripe subscription for the organization.

        Args:
            organization: Organization instance.
            plan_key: One of PAID_PLAN_KEYS (STARTER, PROFESSIONAL, ENTERPRISE).
            billing_interval: ``'monthly'`` or ``'annual'``.

        Returns:
            The Stripe Subscription object.
        """
        _configure_stripe()

        if plan_key not in PAID_PLAN_KEYS:
            raise ValueError(f"Invalid plan key: {plan_key}")

        plan_cfg = PLAN_CONFIG[plan_key]
        price_field = f"stripe_price_{billing_interval}"
        price_id = plan_cfg.get(price_field)
        if not price_id:
            raise ValueError(f"No {billing_interval} price configured for {plan_key}")

        # Ensure customer exists
        customer_id = organization.stripe_customer_id
        if not customer_id:
            customer_id = StripeService.create_customer(organization)

        seat_count = organization.member_count or 1

        sub = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id, "quantity": seat_count}],
            metadata={
                "organization_id": str(organization.id),
                "plan_key": plan_key,
            },
        )

        # Update Organization fields
        Organization.objects.filter(pk=organization.pk).update(
            stripe_subscription_id=sub.id,
            subscription_plan=plan_key.lower(),
            subscription_status="active",
            max_users=plan_cfg["max_users"],
        )
        organization.stripe_subscription_id = sub.id
        organization.subscription_plan = plan_key.lower()
        organization.subscription_status = "active"
        organization.max_users = plan_cfg["max_users"]

        # Sync module access
        ModuleGateService.sync_modules(organization, plan_key)

        logger.info("Created subscription %s (%s) for %s", sub.id, plan_key, organization)
        return sub

    @staticmethod
    def update_subscription(organization, new_plan_key):
        """Upgrade or downgrade an existing subscription with proration.

        Returns the updated Stripe Subscription object.
        """
        _configure_stripe()

        if new_plan_key not in PAID_PLAN_KEYS:
            raise ValueError(f"Invalid plan key: {new_plan_key}")
        if not organization.stripe_subscription_id:
            raise ValueError("Organization does not have an active subscription")

        sub = stripe.Subscription.retrieve(organization.stripe_subscription_id)
        plan_cfg = PLAN_CONFIG[new_plan_key]

        # Determine current billing interval from existing price
        current_item = sub["items"]["data"][0]
        current_price_id = current_item["price"]["id"]
        # Figure out if annual or monthly from the current subscription
        interval = "annual" if "annual" in current_price_id else "monthly"
        new_price_id = plan_cfg.get(f"stripe_price_{interval}")

        updated_sub = stripe.Subscription.modify(
            organization.stripe_subscription_id,
            items=[
                {
                    "id": current_item["id"],
                    "price": new_price_id,
                    "quantity": organization.member_count or 1,
                }
            ],
            proration_behavior="create_prorations",
            metadata={
                "organization_id": str(organization.id),
                "plan_key": new_plan_key,
            },
        )

        Organization.objects.filter(pk=organization.pk).update(
            subscription_plan=new_plan_key.lower(),
            max_users=plan_cfg["max_users"],
        )
        organization.subscription_plan = new_plan_key.lower()
        organization.max_users = plan_cfg["max_users"]

        ModuleGateService.sync_modules(organization, new_plan_key)

        logger.info("Updated subscription to %s for %s", new_plan_key, organization)
        return updated_sub

    @staticmethod
    def cancel_subscription(organization, at_period_end=True):
        """Cancel the organization's subscription.

        By default cancels at the end of the current billing period.
        """
        _configure_stripe()

        if not organization.stripe_subscription_id:
            raise ValueError("Organization does not have an active subscription")

        if at_period_end:
            sub = stripe.Subscription.modify(
                organization.stripe_subscription_id,
                cancel_at_period_end=True,
            )
        else:
            sub = stripe.Subscription.cancel(organization.stripe_subscription_id)

        logger.info("Canceled subscription for %s (at_period_end=%s)", organization, at_period_end)
        return sub

    @staticmethod
    def create_billing_portal_session(organization):
        """Create a Stripe Customer Portal session.

        Returns the portal session URL for redirect.
        """
        _configure_stripe()

        if not organization.stripe_customer_id:
            raise ValueError("Organization does not have a Stripe customer")

        session = stripe.billing_portal.Session.create(
            customer=organization.stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/settings/billing",
        )
        return session.url

    @staticmethod
    def sync_subscription_status(organization):
        """Pull the latest subscription status from Stripe and update the org.

        Called by the weekly reconciliation task and after webhook events.
        """
        _configure_stripe()

        if not organization.stripe_subscription_id:
            return

        sub = stripe.Subscription.retrieve(organization.stripe_subscription_id)

        status_map = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "canceled",
            "unpaid": "past_due",
            "trialing": "trialing",
            "incomplete": "past_due",
            "incomplete_expired": "canceled",
        }
        new_status = status_map.get(sub.status, "canceled")

        # Determine plan from metadata or price ID
        plan_key = sub.metadata.get("plan_key", "").upper()
        if not plan_key or plan_key not in PLAN_CONFIG:
            price_id = sub["items"]["data"][0]["price"]["id"] if sub["items"]["data"] else None
            plan_key = STRIPE_PRICE_TO_PLAN.get(price_id, organization.subscription_plan.upper())

        plan_cfg = PLAN_CONFIG.get(plan_key, {})

        Organization.objects.filter(pk=organization.pk).update(
            subscription_status=new_status,
            subscription_plan=plan_key.lower() if plan_key in PLAN_CONFIG else organization.subscription_plan,
            max_users=plan_cfg.get("max_users", organization.max_users),
        )

        logger.info("Synced subscription status for %s: %s / %s", organization, new_status, plan_key)

    @staticmethod
    def update_seat_count(organization):
        """Update the Stripe subscription quantity when members change.

        Called after a new member is added or removed.
        """
        _configure_stripe()

        if not organization.stripe_subscription_id:
            return

        sub = stripe.Subscription.retrieve(organization.stripe_subscription_id)
        if not sub["items"]["data"]:
            return

        item = sub["items"]["data"][0]
        new_quantity = organization.member_count or 1

        if item["quantity"] != new_quantity:
            stripe.SubscriptionItem.modify(
                item["id"],
                quantity=new_quantity,
                proration_behavior="create_prorations",
            )
            logger.info("Updated seat count to %d for %s", new_quantity, organization)

    @staticmethod
    def handle_trial_conversion(organization, plan_key, billing_interval="monthly"):
        """Convert a trialing organization to a paid subscription.

        Convenience wrapper that ensures the org has a customer and creates
        the subscription, clearing the trial status.
        """
        sub = StripeService.create_subscription(organization, plan_key, billing_interval)

        Organization.objects.filter(pk=organization.pk).update(
            trial_ends_at=None,
        )
        return sub


# ---------------------------------------------------------------------------
# ModuleGateService
# ---------------------------------------------------------------------------


class ModuleGateService:
    """Controls feature/module access based on the organization's plan."""

    @staticmethod
    def check_module_access(organization, module_key):
        """Return True if *organization*'s current plan includes *module_key*."""
        plan_key = organization.subscription_plan.upper()
        plan_cfg = PLAN_CONFIG.get(plan_key)
        if not plan_cfg:
            return False
        return module_key.upper() in plan_cfg["modules"]

    @staticmethod
    def get_available_modules(organization):
        """Return the list of module keys allowed by the org's current plan."""
        plan_key = organization.subscription_plan.upper()
        plan_cfg = PLAN_CONFIG.get(plan_key)
        if not plan_cfg:
            return []
        return list(plan_cfg["modules"])

    @staticmethod
    def check_user_limit(organization):
        """Return True if the organization can add more users."""
        plan_key = organization.subscription_plan.upper()
        plan_cfg = PLAN_CONFIG.get(plan_key)
        if not plan_cfg:
            return False
        return organization.member_count < plan_cfg["max_users"]

    @staticmethod
    def get_plan_limits(organization):
        """Return a dict of all limits for the organization's current plan."""
        plan_key = organization.subscription_plan.upper()
        plan_cfg = PLAN_CONFIG.get(plan_key, {})
        return {
            "plan_key": plan_key,
            "plan_name": plan_cfg.get("name", "Unknown"),
            "max_users": plan_cfg.get("max_users", 0),
            "modules": plan_cfg.get("modules", []),
            "price_monthly_per_user": plan_cfg.get("price_monthly_per_user", 0),
            "price_annual_per_user": plan_cfg.get("price_annual_per_user", 0),
        }

    @staticmethod
    def sync_modules(organization, plan_key):
        """Activate/deactivate modules to match the given plan.

        Activates modules included in the plan, deactivates those that
        aren't (respecting ALWAYS_ACTIVE).
        """
        plan_cfg = PLAN_CONFIG.get(plan_key.upper())
        if not plan_cfg:
            return

        allowed = set(m.lower() for m in plan_cfg["modules"])

        for module_choice in ActiveModule.ModuleKey:
            key = module_choice.value
            is_allowed = key in allowed or key in {m.value for m in ActiveModule.ALWAYS_ACTIVE}

            ActiveModule.objects.update_or_create(
                organization=organization,
                module_key=key,
                defaults={"is_active": is_allowed},
            )
