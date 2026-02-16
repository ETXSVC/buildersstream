"""Tenant signals - auto-setup on organization creation."""
import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ActiveModule, Organization, OrganizationMembership

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Organization)
def setup_new_organization(sender, instance, created, **kwargs):
    """On Organization creation:
    1. Auto-create OrganizationMembership with OWNER role
    2. Activate default modules (PROJECT_CENTER + ANALYTICS)
    3. Create Stripe customer (placeholder)
    """
    if not created:
        return

    # 1. Create OWNER membership (if owner is set and no membership exists yet)
    if instance.owner_id:
        OrganizationMembership.objects.get_or_create(
            user=instance.owner,
            organization=instance,
            defaults={
                "role": OrganizationMembership.Role.OWNER,
                "is_active": True,
                "accepted_at": timezone.now(),
            },
        )

    # 2. Activate always-on modules
    for module_key in ActiveModule.ALWAYS_ACTIVE:
        ActiveModule.objects.get_or_create(
            organization=instance,
            module_key=module_key,
            defaults={"is_active": True},
        )

    # 3. Create Stripe customer (placeholder - implement with Stripe API)
    if not instance.stripe_customer_id:
        _create_stripe_customer(instance)


def _create_stripe_customer(organization):
    """Create a Stripe customer for the organization.

    Placeholder — implement with stripe.Customer.create() when
    Stripe keys are configured.
    """
    stripe_secret = getattr(settings, "STRIPE_SECRET_KEY", "")
    if not stripe_secret:
        logger.info("Stripe not configured, skipping customer creation for %s", organization)
        return

    try:
        import stripe

        stripe.api_key = stripe_secret
        customer = stripe.Customer.create(
            name=organization.name,
            email=organization.email or organization.owner.email,
            metadata={"organization_id": str(organization.id)},
        )
        Organization.objects.filter(pk=organization.pk).update(
            stripe_customer_id=customer.id,
        )
        logger.info("Created Stripe customer %s for %s", customer.id, organization)
    except Exception:
        logger.exception("Failed to create Stripe customer for %s", organization)
