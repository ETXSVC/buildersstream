"""
Celery tasks for the estimating app.

Tasks:
- generate_pdf_proposal: Async PDF generation for a proposal
- send_proposal_email: Send proposal email with PDF attachment
- notify_proposal_signed: Notify assigned user when proposal is signed
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_pdf_proposal(self, proposal_id: str) -> dict:
    """
    Generate a PDF for the given proposal and store it on the model.

    Args:
        proposal_id: UUID string of the Proposal to render.

    Returns:
        dict with 'success' bool and 'proposal_id'.
    """
    from apps.estimating.models import Proposal
    from apps.estimating.services import ExportService

    try:
        proposal = Proposal.objects.select_related(
            'estimate',
            'estimate__organization',
            'template',
        ).prefetch_related(
            'estimate__sections__line_items__cost_item',
            'estimate__sections__line_items__assembly',
        ).get(pk=proposal_id)

        pdf_bytes = ExportService.generate_proposal_pdf(proposal)

        # Store the PDF file on the proposal model
        from django.core.files.base import ContentFile
        filename = f"proposal_{proposal.proposal_number}.pdf"
        proposal.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

        logger.info("PDF generated for proposal %s (%s)", proposal_id, filename)
        return {'success': True, 'proposal_id': proposal_id}

    except Proposal.DoesNotExist:
        logger.error("Proposal %s not found — skipping PDF generation", proposal_id)
        return {'success': False, 'proposal_id': proposal_id, 'error': 'not_found'}

    except Exception as exc:
        logger.exception("PDF generation failed for proposal %s: %s", proposal_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_proposal_email(self, proposal_id: str, recipient_email: str) -> dict:
    """
    Send proposal email to the specified recipient with PDF attachment.

    Args:
        proposal_id: UUID string of the Proposal.
        recipient_email: Destination email address.

    Returns:
        dict with 'success' bool and delivery info.
    """
    from apps.estimating.models import Proposal
    from apps.estimating.services import ExportService

    try:
        proposal = Proposal.objects.select_related(
            'estimate',
            'estimate__organization',
            'estimate__client',
        ).get(pk=proposal_id)

        # Generate PDF if not already stored
        if not proposal.pdf_file:
            pdf_bytes = ExportService.generate_proposal_pdf(proposal)
        else:
            pdf_bytes = proposal.pdf_file.read()

        # Build public proposal URL
        from django.conf import settings
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        public_url = f"{base_url}/proposals/{proposal.public_token}"

        subject = f"Proposal {proposal.proposal_number} from {proposal.estimate.organization.name}"
        body = (
            f"Dear {proposal.contact_name or 'Client'},\n\n"
            f"Please find attached proposal {proposal.proposal_number}.\n\n"
            f"You can also view and sign it online at:\n{public_url}\n\n"
            f"This proposal is valid until {proposal.valid_until}.\n\n"
            f"Thank you,\n{proposal.estimate.organization.name}"
        )

        from django.core.mail import EmailMessage
        email = EmailMessage(
            subject=subject,
            body=body,
            to=[recipient_email],
        )
        email.attach(
            f"proposal_{proposal.proposal_number}.pdf",
            pdf_bytes,
            'application/pdf',
        )
        email.send(fail_silently=False)

        logger.info(
            "Proposal email sent for %s to %s",
            proposal_id,
            recipient_email,
        )
        return {'success': True, 'proposal_id': proposal_id, 'recipient': recipient_email}

    except Proposal.DoesNotExist:
        logger.error("Proposal %s not found — skipping email", proposal_id)
        return {'success': False, 'proposal_id': proposal_id, 'error': 'not_found'}

    except Exception as exc:
        logger.exception(
            "Failed to send proposal email for %s to %s: %s",
            proposal_id,
            recipient_email,
            exc,
        )
        raise self.retry(exc=exc)


@shared_task
def notify_proposal_signed(proposal_id: str) -> dict:
    """
    Notify the estimate's assigned user when a proposal is signed.

    Args:
        proposal_id: UUID string of the signed Proposal.

    Returns:
        dict with 'success' bool.
    """
    from apps.estimating.models import Proposal

    try:
        proposal = Proposal.objects.select_related(
            'estimate',
            'estimate__assigned_to',
            'estimate__organization',
        ).get(pk=proposal_id)

        assigned_user = proposal.estimate.assigned_to
        if not assigned_user or not assigned_user.email:
            logger.info(
                "No assigned user for estimate %s — skipping signed notification",
                proposal.estimate_id,
            )
            return {'success': True, 'skipped': True}

        subject = (
            f"Proposal {proposal.proposal_number} has been signed!"
        )
        body = (
            f"Hi {assigned_user.get_full_name() or assigned_user.email},\n\n"
            f"Great news! Proposal {proposal.proposal_number} has been signed "
            f"by {proposal.signed_by_name or 'the client'}.\n\n"
            f"Project: {proposal.estimate.name}\n"
            f"Organization: {proposal.estimate.organization.name}\n\n"
            f"You can now proceed to contract creation."
        )

        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[assigned_user.email],
            fail_silently=True,
        )

        logger.info(
            "Signed notification sent to %s for proposal %s",
            assigned_user.email,
            proposal_id,
        )
        return {'success': True, 'notified': assigned_user.email}

    except Proposal.DoesNotExist:
        logger.error("Proposal %s not found — skipping signed notification", proposal_id)
        return {'success': False, 'error': 'not_found'}

    except Exception as exc:
        logger.exception(
            "Failed to send signed notification for proposal %s: %s",
            proposal_id,
            exc,
        )
        return {'success': False, 'error': str(exc)}
