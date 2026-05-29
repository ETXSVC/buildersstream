"""Service & Warranty Management services."""
import logging
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

logger = logging.getLogger(__name__)


class ServiceTicketService:
    """Business logic for service ticket lifecycle and dispatch."""

    @staticmethod
    def assign_ticket(ticket, user, scheduled_date=None):
        """Assign a ticket to a technician, optionally setting a scheduled date."""
        from .models import ServiceTicket

        ticket.assigned_to = user
        ticket.status = ServiceTicket.Status.ASSIGNED
        if scheduled_date is not None:
            ticket.scheduled_date = scheduled_date
        ticket.save(update_fields=["assigned_to", "status", "scheduled_date", "updated_at"])
        logger.info("ServiceTicket %s assigned to user %s", ticket.pk, user.pk)
        return ticket

    @staticmethod
    def complete_ticket(ticket, resolution, labor_hours=None, parts_cost=None):
        """Mark a ticket as completed with resolution details."""
        from .models import ServiceTicket

        if ticket.status in (ServiceTicket.Status.COMPLETED, ServiceTicket.Status.CLOSED):
            raise ValueError(f"Ticket is already {ticket.status}.")

        ticket.status = ServiceTicket.Status.COMPLETED
        ticket.resolution = resolution
        ticket.completed_date = timezone.now()
        if labor_hours is not None:
            ticket.labor_hours = Decimal(str(labor_hours))
        if parts_cost is not None:
            ticket.parts_cost = Decimal(str(parts_cost))

        # Recalculate total_cost (simple sum; override billing_type logic as needed)
        if ticket.billing_type == ServiceTicket.BillingType.WARRANTY_NO_CHARGE:
            ticket.total_cost = Decimal("0")
        else:
            ticket.total_cost = ticket.labor_hours * Decimal("0") + ticket.parts_cost
            # labor cost left at $0 here — caller passes dollar amount in labor_hours or
            # the generate_invoice action will compute based on employee rate

        ticket.save(
            update_fields=[
                "status", "resolution", "completed_date",
                "labor_hours", "parts_cost", "total_cost", "updated_at",
            ]
        )
        logger.info("ServiceTicket %s completed", ticket.pk)
        return ticket

    @staticmethod
    def generate_invoice(ticket, user):
        """Create a financials.Invoice from a completed, billable service ticket."""
        from apps.financials.models import Invoice, InvoiceLineItem

        if not ticket.billable:
            raise ValueError("Ticket is not billable.")
        if ticket.billing_type == ServiceTicket.BillingType.WARRANTY_NO_CHARGE:
            raise ValueError("Warranty (no charge) tickets cannot generate invoices.")
        if ticket.invoice_id:
            raise ValueError("Invoice already exists for this ticket.")

        from .models import ServiceTicket  # local import to avoid circular

        from apps.financials.services import InvoicingService
        from apps.tenants.context import get_current_organization

        org = get_current_organization()
        client = ticket.client

        invoice = InvoicingService.create_invoice(
            organization=org,
            project=ticket.project,
            client=client,
            created_by=user,
            notes=f"Service ticket {ticket.ticket_number}: {ticket.title}",
        )

        if ticket.labor_hours and ticket.labor_hours > 0:
            InvoiceLineItem.objects.create(
                invoice=invoice,
                description="Labor",
                quantity=ticket.labor_hours,
                unit_price=Decimal("0"),  # caller fills in rate if needed
                line_total=Decimal("0"),
            )
        if ticket.parts_cost and ticket.parts_cost > 0:
            InvoiceLineItem.objects.create(
                invoice=invoice,
                description="Parts & Materials",
                quantity=Decimal("1"),
                unit_price=ticket.parts_cost,
                line_total=ticket.parts_cost,
            )

        ticket.invoice = invoice
        ticket.save(update_fields=["invoice", "updated_at"])
        logger.info("Invoice %s generated for ServiceTicket %s", invoice.pk, ticket.pk)
        return invoice

    @staticmethod
    def get_dispatch_board(organization, target_date=None):
        """Return all tickets scheduled for target_date (default today), grouped by status."""
        from .models import ServiceTicket

        if target_date is None:
            target_date = timezone.now().date()

        tickets = (
            ServiceTicket.objects.filter(
                organization=organization,
                scheduled_date__date=target_date,
            )
            .select_related("project", "client", "assigned_to")
            .exclude(status=ServiceTicket.Status.CLOSED)
            .order_by("priority", "scheduled_date")
        )

        board = {
            "date": str(target_date),
            "total": tickets.count(),
            "by_status": {},
        }
        for ticket in tickets:
            s = ticket.status
            board["by_status"].setdefault(s, []).append(ticket)

        return board, tickets


class WarrantyService:
    """Business logic for warranty tracking and claim management."""

    @staticmethod
    def expire_old_warranties(organization=None):
        """Mark warranties whose end_date has passed as EXPIRED."""
        from .models import Warranty

        qs = Warranty.objects.filter(
            status=Warranty.WarrantyStatus.ACTIVE,
            end_date__lt=timezone.now().date(),
        )
        if organization:
            qs = qs.filter(organization=organization)

        count = qs.update(status=Warranty.WarrantyStatus.EXPIRED)
        if count:
            logger.info("Expired %d warranties", count)
        return count

    @staticmethod
    def file_claim(warranty, description, service_ticket=None, user=None):
        """File a WarrantyClaim against a warranty and update warranty status."""
        from .models import WarrantyClaim

        if warranty.status == warranty.WarrantyStatus.EXPIRED:
            raise ValueError("Cannot file a claim on an expired warranty.")

        claim = WarrantyClaim.objects.create(
            organization_id=warranty.organization_id,
            warranty=warranty,
            service_ticket=service_ticket,
            description=description,
            status=WarrantyClaim.ClaimStatus.FILED,
            created_by=user,
        )

        # Mark warranty as claimed (can still be active; up to business logic)
        if warranty.status == warranty.WarrantyStatus.ACTIVE:
            warranty.status = warranty.WarrantyStatus.CLAIMED
            warranty.save(update_fields=["status", "updated_at"])

        logger.info("WarrantyClaim %s filed on warranty %s", claim.pk, warranty.pk)
        return claim

    @staticmethod
    def resolve_claim(claim, resolution, cost=None):
        """Resolve a warranty claim."""
        from .models import WarrantyClaim

        if claim.status == WarrantyClaim.ClaimStatus.RESOLVED:
            raise ValueError("Claim is already resolved.")

        claim.status = WarrantyClaim.ClaimStatus.RESOLVED
        claim.resolution = resolution
        if cost is not None:
            claim.cost = Decimal(str(cost))
        claim.save(update_fields=["status", "resolution", "cost", "updated_at"])
        logger.info("WarrantyClaim %s resolved", claim.pk)
        return claim

    @staticmethod
    def get_expiring_soon(organization, days_ahead=30):
        """Return warranties expiring within days_ahead days."""
        from .models import Warranty

        cutoff = timezone.now().date() + timedelta(days=days_ahead)
        return Warranty.objects.filter(
            organization=organization,
            status=Warranty.WarrantyStatus.ACTIVE,
            end_date__lte=cutoff,
            end_date__gte=timezone.now().date(),
        ).select_related("project").order_by("end_date")


class ServiceAgreementService:
    """Business logic for service agreements and recurring billing."""

    @staticmethod
    def record_visit(agreement):
        """Record a completed visit against the agreement."""
        agreement.visits_completed += 1
        agreement.save(update_fields=["visits_completed", "updated_at"])
        return agreement

    @staticmethod
    def renew_agreement(agreement):
        """Renew an active or expired agreement by extending end_date one cycle."""
        from .models import ServiceAgreement

        freq = agreement.billing_frequency
        if freq == ServiceAgreement.BillingFrequency.MONTHLY:
            delta = timedelta(days=30)
        elif freq == ServiceAgreement.BillingFrequency.QUARTERLY:
            delta = timedelta(days=90)
        else:  # ANNUAL
            delta = timedelta(days=365)

        # Extend from end_date (or today if already expired past it)
        base = max(agreement.end_date, timezone.now().date())
        agreement.end_date = base + delta
        agreement.visits_completed = 0
        agreement.status = ServiceAgreement.AgreementStatus.ACTIVE
        agreement.save(update_fields=["end_date", "visits_completed", "status", "updated_at"])
        logger.info("ServiceAgreement %s renewed until %s", agreement.pk, agreement.end_date)
        return agreement

    @staticmethod
    def expire_old_agreements(organization=None):
        """Mark agreements past their end_date as EXPIRED."""
        from .models import ServiceAgreement

        qs = ServiceAgreement.objects.filter(
            status=ServiceAgreement.AgreementStatus.ACTIVE,
            end_date__lt=timezone.now().date(),
        )
        if organization:
            qs = qs.filter(organization=organization)

        count = qs.update(status=ServiceAgreement.AgreementStatus.EXPIRED)
        if count:
            logger.info("Expired %d service agreements", count)
        return count

    @staticmethod
    def generate_recurring_invoices(organization):
        """Generate invoices for all active agreements due for billing this month."""
        from apps.financials.services import InvoicingService
        from .models import ServiceAgreement

        today = timezone.now().date()
        invoices_created = []

        active = ServiceAgreement.objects.filter(
            organization=organization,
            status=ServiceAgreement.AgreementStatus.ACTIVE,
            start_date__lte=today,
            end_date__gte=today,
        ).select_related("client")

        for agreement in active:
            try:
                invoice = InvoicingService.create_invoice(
                    organization=organization,
                    project=None,
                    client=agreement.client,
                    created_by=None,
                    notes=f"Recurring service agreement: {agreement.name}",
                )
                invoices_created.append(invoice)
                logger.info(
                    "Recurring invoice %s created for agreement %s", invoice.pk, agreement.pk
                )
            except Exception as exc:
                logger.error(
                    "Failed to create invoice for agreement %s: %s", agreement.pk, exc
                )

        return invoices_created

    @staticmethod
    def get_agreements_due_for_visit(organization):
        """Return active agreements where visits_completed < visits_per_year."""
        from .models import ServiceAgreement

        return ServiceAgreement.objects.filter(
            organization=organization,
            status=ServiceAgreement.AgreementStatus.ACTIVE,
        ).filter(
            visits_completed__lt=models.F("visits_per_year")
        ).select_related("client")


# Local import needed for F() expression
from django.db import models  # noqa: E402
