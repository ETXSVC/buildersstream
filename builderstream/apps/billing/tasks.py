"""Billing Celery tasks — trial management and subscription sync."""
import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(name="billing.check_expiring_trials")
def check_expiring_trials():
    """Daily task: send reminder emails for trials ending within 3 days."""
    from apps.tenants.models import Organization

    cutoff = timezone.now() + timedelta(days=3)
    expiring = Organization.objects.filter(
        subscription_status="trialing",
        trial_ends_at__isnull=False,
        trial_ends_at__lte=cutoff,
        trial_ends_at__gt=timezone.now(),
        is_active=True,
    ).select_related("owner")

    count = 0
    for org in expiring:
        try:
            days_left = (org.trial_ends_at - timezone.now()).days
            send_mail(
                subject=f"BuilderStream — Your trial ends in {days_left} day{'s' if days_left != 1 else ''}",
                message=(
                    f"Hi {org.owner.first_name},\n\n"
                    f"Your BuilderStream trial for {org.name} ends in {days_left} days. "
                    "Subscribe now to keep access to all your data and features.\n\n"
                    "Visit your billing settings to choose a plan.\n\n"
                    "The BuilderStream Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[org.owner.email],
                fail_silently=True,
            )
            count += 1
        except Exception:
            logger.exception("Failed to send trial reminder for %s", org)

    logger.info("Sent %d trial expiration reminders", count)
    return count


@shared_task(name="billing.expire_trials")
def expire_trials():
    """Daily task: deactivate orgs past trial_ends_at that haven't subscribed."""
    from apps.tenants.models import Organization
    from .models import SubscriptionEvent

    expired = Organization.objects.filter(
        subscription_status="trialing",
        trial_ends_at__isnull=False,
        trial_ends_at__lte=timezone.now(),
        is_active=True,
    ).select_related("owner")

    count = 0
    for org in expired:
        Organization.objects.filter(pk=org.pk).update(
            subscription_status="canceled",
        )

        # Create audit event
        SubscriptionEvent.objects.create(
            organization=org,
            event_type=SubscriptionEvent.EventType.TRIAL_ENDED,
            stripe_event_id=f"trial_expired_{org.pk}_{timezone.now().isoformat()}",
            data={"reason": "trial_expired", "trial_ends_at": str(org.trial_ends_at)},
        )

        try:
            send_mail(
                subject="BuilderStream — Your trial has ended",
                message=(
                    f"Hi {org.owner.first_name},\n\n"
                    f"Your BuilderStream trial for {org.name} has ended. "
                    "Your data is preserved for 30 days. Subscribe to regain "
                    "full access.\n\nThe BuilderStream Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[org.owner.email],
                fail_silently=True,
            )
        except Exception:
            logger.exception("Failed to send trial expiration email for %s", org)

        count += 1

    logger.info("Expired %d trials", count)
    return count


@shared_task(name="billing.sync_all_subscriptions")
def sync_all_subscriptions():
    """Weekly task: reconcile all active subscriptions with Stripe."""
    from apps.tenants.models import Organization
    from .services import StripeService

    orgs = Organization.objects.filter(
        stripe_subscription_id__isnull=False,
        subscription_status__in=["active", "past_due", "trialing"],
        is_active=True,
    )

    synced = 0
    errors = 0
    for org in orgs:
        try:
            StripeService.sync_subscription_status(org)
            synced += 1
        except Exception:
            logger.exception("Failed to sync subscription for %s", org)
            errors += 1

    logger.info("Synced %d subscriptions (%d errors)", synced, errors)
    return {"synced": synced, "errors": errors}
