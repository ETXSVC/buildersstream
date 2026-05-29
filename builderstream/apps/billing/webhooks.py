"""Stripe webhook handler.

Receives Stripe events, verifies the signature, and dispatches to
the appropriate handler.  Creates a SubscriptionEvent audit record
for every processed event.

Also handles payment_intent.succeeded for financials.Invoice client payments.
"""
import logging
from datetime import datetime, timezone as dt_tz
from decimal import Decimal

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.tenants.models import Organization

from .models import Invoice, SubscriptionEvent
from .plans import PLAN_CONFIG, STRIPE_PRICE_TO_PLAN
from .services import ModuleGateService, StripeService

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """Handle incoming Stripe webhook events.

    Authentication is handled via Stripe signature verification,
    not Django REST Framework auth classes.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            logger.warning("Invalid Stripe webhook payload")
            return JsonResponse({"error": "Invalid payload"}, status=400)
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return JsonResponse({"error": "Invalid signature"}, status=400)

        event_type = event["type"]
        handler = self._get_handler(event_type)

        if handler:
            try:
                handler(event)
            except Exception:
                logger.exception("Error handling Stripe event %s (%s)", event["id"], event_type)
                return JsonResponse({"error": "Handler error"}, status=500)
        else:
            logger.debug("Unhandled Stripe event type: %s", event_type)

        return JsonResponse({"status": "ok"})

    # -- Dispatcher ---------------------------------------------------------

    def _get_handler(self, event_type):
        handlers = {
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "customer.subscription.trial_will_end": self._handle_trial_will_end,
            # Financial invoice online payments
            "payment_intent.succeeded": self._handle_invoice_payment_intent_succeeded,
        }
        return handlers.get(event_type)

    # -- Helpers ------------------------------------------------------------

    @staticmethod
    def _get_org_from_event(event):
        """Resolve the Organization from the Stripe event metadata or customer."""
        data_obj = event["data"]["object"]

        # Try metadata first
        org_id = data_obj.get("metadata", {}).get("organization_id")
        if org_id:
            try:
                return Organization.objects.get(pk=org_id)
            except Organization.DoesNotExist:
                pass

        # Fall back to customer ID lookup
        customer_id = data_obj.get("customer")
        if customer_id:
            try:
                return Organization.objects.get(stripe_customer_id=customer_id)
            except Organization.DoesNotExist:
                pass

        logger.error("Could not resolve organization for event %s", event["id"])
        return None

    @staticmethod
    def _log_event(org, event, event_type_choice):
        """Create a SubscriptionEvent audit record (idempotent on stripe_event_id)."""
        SubscriptionEvent.objects.get_or_create(
            stripe_event_id=event["id"],
            defaults={
                "organization": org,
                "event_type": event_type_choice,
                "data": event["data"],
            },
        )

    # -- Event handlers -----------------------------------------------------

    def _handle_subscription_created(self, event):
        org = self._get_org_from_event(event)
        if not org:
            return

        sub = event["data"]["object"]
        plan_key = self._resolve_plan_key(sub)
        plan_cfg = PLAN_CONFIG.get(plan_key, {})

        Organization.objects.filter(pk=org.pk).update(
            stripe_subscription_id=sub["id"],
            subscription_plan=plan_key.lower(),
            subscription_status=sub["status"],
            max_users=plan_cfg.get("max_users", org.max_users),
        )

        ModuleGateService.sync_modules(org, plan_key)
        self._log_event(org, event, SubscriptionEvent.EventType.CREATED)
        logger.info("Subscription created for %s: %s", org, plan_key)

    def _handle_subscription_updated(self, event):
        org = self._get_org_from_event(event)
        if not org:
            return

        sub = event["data"]["object"]
        plan_key = self._resolve_plan_key(sub)
        plan_cfg = PLAN_CONFIG.get(plan_key, {})

        status_map = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "canceled",
            "unpaid": "past_due",
            "trialing": "trialing",
            "incomplete": "past_due",
            "incomplete_expired": "canceled",
        }

        Organization.objects.filter(pk=org.pk).update(
            subscription_plan=plan_key.lower(),
            subscription_status=status_map.get(sub["status"], "canceled"),
            max_users=plan_cfg.get("max_users", org.max_users),
        )

        ModuleGateService.sync_modules(org, plan_key)
        self._log_event(org, event, SubscriptionEvent.EventType.UPDATED)
        logger.info("Subscription updated for %s: %s / %s", org, plan_key, sub["status"])

    def _handle_subscription_deleted(self, event):
        org = self._get_org_from_event(event)
        if not org:
            return

        Organization.objects.filter(pk=org.pk).update(
            subscription_status="canceled",
        )

        self._log_event(org, event, SubscriptionEvent.EventType.CANCELED)
        logger.info("Subscription canceled for %s", org)

        # Send data retention notice
        try:
            send_mail(
                subject="BuilderStream — Your subscription has been canceled",
                message=(
                    f"Hi {org.owner.first_name},\n\n"
                    f"Your BuilderStream subscription for {org.name} has been canceled. "
                    "Your data will be retained for 30 days. To reactivate, visit your "
                    "billing settings.\n\nThe BuilderStream Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[org.owner.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send cancellation email for %s", org)

    def _handle_payment_succeeded(self, event):
        invoice_data = event["data"]["object"]
        customer_id = invoice_data.get("customer")

        try:
            org = Organization.objects.get(stripe_customer_id=customer_id)
        except Organization.DoesNotExist:
            logger.error("No org for customer %s on payment_succeeded", customer_id)
            return

        # Upsert invoice record
        period_start = None
        period_end = None
        if invoice_data.get("period_start"):
            period_start = datetime.fromtimestamp(invoice_data["period_start"], tz=dt_tz.utc)
        if invoice_data.get("period_end"):
            period_end = datetime.fromtimestamp(invoice_data["period_end"], tz=dt_tz.utc)

        Invoice.objects.update_or_create(
            stripe_invoice_id=invoice_data["id"],
            defaults={
                "organization": org,
                "amount_due": invoice_data.get("amount_due", 0),
                "amount_paid": invoice_data.get("amount_paid", 0),
                "currency": invoice_data.get("currency", "usd"),
                "status": "paid",
                "period_start": period_start,
                "period_end": period_end,
                "hosted_invoice_url": invoice_data.get("hosted_invoice_url", ""),
                "pdf_url": invoice_data.get("invoice_pdf", ""),
            },
        )

        # Ensure org is marked active
        Organization.objects.filter(pk=org.pk).update(subscription_status="active")

        self._log_event(org, event, SubscriptionEvent.EventType.PAYMENT_SUCCEEDED)
        logger.info("Payment succeeded for %s: %s", org, invoice_data["id"])

    def _handle_payment_failed(self, event):
        invoice_data = event["data"]["object"]
        customer_id = invoice_data.get("customer")

        try:
            org = Organization.objects.get(stripe_customer_id=customer_id)
        except Organization.DoesNotExist:
            logger.error("No org for customer %s on payment_failed", customer_id)
            return

        Organization.objects.filter(pk=org.pk).update(subscription_status="past_due")

        self._log_event(org, event, SubscriptionEvent.EventType.PAYMENT_FAILED)
        logger.info("Payment failed for %s", org)

        # Send failure notification
        try:
            send_mail(
                subject="BuilderStream — Payment failed",
                message=(
                    f"Hi {org.owner.first_name},\n\n"
                    f"We were unable to process payment for {org.name}. "
                    "Please update your payment method in billing settings "
                    "to avoid service interruption.\n\nThe BuilderStream Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[org.owner.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send payment failure email for %s", org)

    def _handle_trial_will_end(self, event):
        org = self._get_org_from_event(event)
        if not org:
            return

        self._log_event(org, event, SubscriptionEvent.EventType.TRIAL_ENDING)
        logger.info("Trial ending soon for %s", org)

        try:
            send_mail(
                subject="BuilderStream — Your trial ends in 3 days",
                message=(
                    f"Hi {org.owner.first_name},\n\n"
                    f"Your BuilderStream trial for {org.name} ends in 3 days. "
                    "Subscribe now to keep access to all your data and features.\n\n"
                    "The BuilderStream Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[org.owner.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send trial ending email for %s", org)

    def _handle_invoice_payment_intent_succeeded(self, event):
        """Auto-record a payment on a financials.Invoice when client pays online via Stripe."""
        from datetime import date

        from apps.financials.models import Invoice as FinancialInvoice
        from apps.financials.services import InvoicingService

        pi = event["data"]["object"]
        pi_id = pi.get("id", "")
        invoice_id = pi.get("metadata", {}).get("invoice_id")

        if not invoice_id:
            logger.debug(
                "payment_intent.succeeded: no invoice_id in metadata (pi=%s), skipping",
                pi_id,
            )
            return

        try:
            invoice = FinancialInvoice.objects.get(
                pk=invoice_id, stripe_payment_intent_id=pi_id
            )
        except FinancialInvoice.DoesNotExist:
            logger.warning(
                "payment_intent.succeeded: no matching financials invoice (pi=%s, id=%s)",
                pi_id,
                invoice_id,
            )
            return

        if invoice.status == "paid":
            logger.info(
                "payment_intent.succeeded: invoice %s already paid, skipping",
                invoice.invoice_number,
            )
            return

        amount_received = Decimal(str(pi.get("amount_received", 0))) / Decimal("100")
        if amount_received <= 0:
            logger.warning(
                "payment_intent.succeeded: zero amount_received for pi %s", pi_id
            )
            return

        InvoicingService.record_payment(
            invoice=invoice,
            amount=amount_received,
            payment_date=date.today(),
            payment_method="card",
            reference_number=pi_id,
            notes=f"Paid online via Stripe ({pi_id})",
        )
        logger.info(
            "payment_intent.succeeded: recorded $%.2f payment for invoice %s",
            amount_received,
            invoice.invoice_number,
        )

    # -- Plan resolution helpers --------------------------------------------

    @staticmethod
    def _resolve_plan_key(subscription_obj):
        """Determine the plan key from a Stripe subscription object."""
        # Check metadata first
        plan_key = subscription_obj.get("metadata", {}).get("plan_key", "").upper()
        if plan_key and plan_key in PLAN_CONFIG:
            return plan_key

        # Fall back to price ID lookup
        items = subscription_obj.get("items", {}).get("data", [])
        if items:
            price_id = items[0].get("price", {}).get("id", "")
            plan_key = STRIPE_PRICE_TO_PLAN.get(price_id, "")
            if plan_key:
                return plan_key

        return "TRIAL"
