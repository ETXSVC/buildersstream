"""Account Celery tasks for async email operations."""
import logging
import uuid

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, user_id):
    """Send email verification link to user."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("User %s not found for verification email", user_id)
        return

    if user.email_verified:
        return

    if not user.email_verification_token:
        user.email_verification_token = uuid.uuid4()
        user.save(update_fields=["email_verification_token"])

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    verify_url = f"{frontend_url}/verify-email?token={user.email_verification_token}"

    subject = "Verify your BuilderStream email"
    message = (
        f"Hi {user.first_name},\n\n"
        f"Please verify your email by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"Thanks,\nThe BuilderStream Team"
    )

    try:
        html_message = render_to_string("emails/verification.html", {
            "user": user,
            "verify_url": verify_url,
        })
    except Exception:
        html_message = None

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
    logger.info("Verification email sent to %s", user.email)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id, token):
    """Send password reset link to user."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("User %s not found for password reset email", user_id)
        return

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    reset_url = f"{frontend_url}/reset-password?token={token}"

    subject = "Reset your BuilderStream password"
    message = (
        f"Hi {user.first_name},\n\n"
        f"Reset your password by clicking the link below:\n\n"
        f"{reset_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"The BuilderStream Team"
    )

    try:
        html_message = render_to_string("emails/password_reset.html", {
            "user": user,
            "reset_url": reset_url,
        })
    except Exception:
        html_message = None

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
    logger.info("Password reset email sent to %s", user.email)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_invitation_email(self, membership_id):
    """Send organization invitation email."""
    from apps.tenants.models import OrganizationMembership

    try:
        membership = OrganizationMembership.objects.select_related(
            "organization", "user", "invited_by"
        ).get(id=membership_id)
    except OrganizationMembership.DoesNotExist:
        logger.error("Membership %s not found for invitation email", membership_id)
        return

    if not membership.invitation_token:
        membership.invitation_token = uuid.uuid4()
        membership.save(update_fields=["invitation_token"])

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    accept_url = f"{frontend_url}/invite/accept/{membership.invitation_token}"

    inviter_name = (
        membership.invited_by.get_full_name() if membership.invited_by else "A team member"
    )
    org_name = membership.organization.name
    recipient_email = membership.user.email

    subject = f"You've been invited to join {org_name} on BuilderStream"
    message = (
        f"Hi,\n\n"
        f"{inviter_name} has invited you to join {org_name} on BuilderStream.\n\n"
        f"Accept the invitation: {accept_url}\n\n"
        f"The BuilderStream Team"
    )

    try:
        html_message = render_to_string("emails/invitation.html", {
            "inviter_name": inviter_name,
            "org_name": org_name,
            "accept_url": accept_url,
        })
    except Exception:
        html_message = None

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=False,
    )
    logger.info("Invitation email sent to %s for org %s", recipient_email, org_name)
