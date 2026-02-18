"""Tests for Service & Warranty Management (Section 15)."""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.accounts.models import User
from apps.tenants.models import Organization, OrganizationMembership
from apps.tenants.context import tenant_context


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="service_test@example.com",
        password="pass1234!",
        first_name="Service",
        last_name="Tester",
    )


@pytest.fixture
def org(db, user):
    org = Organization.objects.create(
        name="Service Test Co",
        slug="service-test-co",
        owner=user,
    )
    return org


@pytest.fixture
def contact(db, org, user):
    """Create a CRM contact for use as a client."""
    from apps.crm.models import Contact
    with tenant_context(org):
        return Contact.objects.create(
            organization=org,
            created_by=user,
            first_name="Client",
            last_name="Contact",
            email="client@example.com",
        )


@pytest.fixture
def project(db, org, user, contact):
    from apps.projects.models import Project
    with tenant_context(org):
        return Project.objects.create(
            organization=org,
            created_by=user,
            name="Test Project",
            status="production",
            client=contact,
        )


@pytest.fixture
def ticket(db, org, user, project, contact):
    from apps.service.models import ServiceTicket
    with tenant_context(org):
        return ServiceTicket.objects.create(
            organization=org,
            created_by=user,
            project=project,
            client=contact,
            title="Fix leaky faucet",
            description="Client reports leak under sink",
            priority=ServiceTicket.Priority.NORMAL,
            status=ServiceTicket.Status.NEW,
            ticket_type=ServiceTicket.TicketType.SERVICE_CALL,
            billable=True,
            billing_type=ServiceTicket.BillingType.TIME_AND_MATERIAL,
        )


@pytest.fixture
def warranty(db, org, user, project):
    from apps.service.models import Warranty
    today = date.today()
    with tenant_context(org):
        return Warranty.objects.create(
            organization=org,
            created_by=user,
            project=project,
            warranty_type=Warranty.WarrantyType.WORKMANSHIP,
            description="1-year workmanship warranty",
            coverage_details="All labor performed by our crews",
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=335),
            status=Warranty.WarrantyStatus.ACTIVE,
        )


@pytest.fixture
def agreement(db, org, user, contact):
    from apps.service.models import ServiceAgreement
    today = date.today()
    with tenant_context(org):
        return ServiceAgreement.objects.create(
            organization=org,
            created_by=user,
            client=contact,
            name="Annual Maintenance Agreement",
            agreement_type=ServiceAgreement.AgreementType.MAINTENANCE,
            start_date=today,
            end_date=today + timedelta(days=365),
            billing_frequency=ServiceAgreement.BillingFrequency.MONTHLY,
            billing_amount=Decimal("199.00"),
            visits_per_year=12,
            status=ServiceAgreement.AgreementStatus.ACTIVE,
        )


# ---------------------------------------------------------------------------
# ServiceTicket tests
# ---------------------------------------------------------------------------

class TestServiceTicketModel:
    def test_ticket_number_auto_generated(self, db, org, user):
        from apps.service.models import ServiceTicket
        with tenant_context(org):
            t = ServiceTicket.objects.create(
                organization=org,
                created_by=user,
                title="Test ticket",
                description="desc",
            )
        year = timezone.now().year
        assert t.ticket_number.startswith(f"SVC-{year}-")

    def test_ticket_number_sequential(self, db, org, user):
        from apps.service.models import ServiceTicket
        with tenant_context(org):
            t1 = ServiceTicket.objects.create(
                organization=org, created_by=user, title="T1", description="d"
            )
            t2 = ServiceTicket.objects.create(
                organization=org, created_by=user, title="T2", description="d"
            )
        seq1 = int(t1.ticket_number.rsplit("-", 1)[-1])
        seq2 = int(t2.ticket_number.rsplit("-", 1)[-1])
        assert seq2 == seq1 + 1

    def test_str_representation(self, ticket):
        assert ticket.ticket_number in str(ticket)
        assert "Fix leaky faucet" in str(ticket)


class TestServiceTicketService:
    def test_assign_ticket(self, db, org, user, ticket):
        from apps.service.models import ServiceTicket
        from apps.service.services import ServiceTicketService

        with tenant_context(org):
            updated = ServiceTicketService.assign_ticket(ticket, user)

        assert updated.status == ServiceTicket.Status.ASSIGNED
        assert updated.assigned_to == user

    def test_assign_with_scheduled_date(self, db, org, user, ticket):
        from apps.service.services import ServiceTicketService

        scheduled = timezone.now() + timedelta(days=2)
        with tenant_context(org):
            updated = ServiceTicketService.assign_ticket(ticket, user, scheduled_date=scheduled)

        assert updated.scheduled_date == scheduled

    def test_complete_ticket(self, db, org, user, ticket):
        from apps.service.models import ServiceTicket
        from apps.service.services import ServiceTicketService

        with tenant_context(org):
            updated = ServiceTicketService.complete_ticket(
                ticket,
                resolution="Replaced P-trap",
                labor_hours=Decimal("2.5"),
                parts_cost=Decimal("45.00"),
            )

        assert updated.status == ServiceTicket.Status.COMPLETED
        assert updated.resolution == "Replaced P-trap"
        assert updated.labor_hours == Decimal("2.5")
        assert updated.parts_cost == Decimal("45.00")
        assert updated.completed_date is not None

    def test_complete_already_completed_raises(self, db, org, user, ticket):
        from apps.service.models import ServiceTicket
        from apps.service.services import ServiceTicketService

        ticket.status = ServiceTicket.Status.COMPLETED
        ticket.save()

        with tenant_context(org):
            with pytest.raises(ValueError, match="already"):
                ServiceTicketService.complete_ticket(ticket, resolution="done")

    def test_complete_warranty_no_charge(self, db, org, user, ticket):
        from apps.service.models import ServiceTicket
        from apps.service.services import ServiceTicketService

        ticket.billing_type = ServiceTicket.BillingType.WARRANTY_NO_CHARGE
        ticket.save()

        with tenant_context(org):
            updated = ServiceTicketService.complete_ticket(
                ticket, resolution="Warranty repair", parts_cost=Decimal("100")
            )

        assert updated.total_cost == Decimal("0")

    def test_dispatch_board_returns_today(self, db, org, user, ticket):
        from apps.service.services import ServiceTicketService

        # Schedule ticket for today
        ticket.scheduled_date = timezone.now()
        ticket.save()

        with tenant_context(org):
            board, qs = ServiceTicketService.get_dispatch_board(org)

        assert board["total"] == 1


# ---------------------------------------------------------------------------
# Warranty tests
# ---------------------------------------------------------------------------

class TestWarrantyModel:
    def test_is_active_property(self, warranty):
        assert warranty.is_active is True

    def test_expired_warranty_not_active(self, db, org, user, project):
        from apps.service.models import Warranty
        with tenant_context(org):
            w = Warranty.objects.create(
                organization=org, created_by=user, project=project,
                warranty_type=Warranty.WarrantyType.WORKMANSHIP,
                description="old warranty",
                coverage_details="x",
                start_date=date.today() - timedelta(days=400),
                end_date=date.today() - timedelta(days=35),
                status=Warranty.WarrantyStatus.ACTIVE,
            )
        assert w.is_active is False


class TestWarrantyService:
    def test_file_claim(self, db, org, user, warranty, ticket):
        from apps.service.models import Warranty, WarrantyClaim
        from apps.service.services import WarrantyService

        with tenant_context(org):
            claim = WarrantyService.file_claim(
                warranty, "Roof is leaking", service_ticket=ticket, user=user
            )

        assert claim.status == WarrantyClaim.ClaimStatus.FILED
        warranty.refresh_from_db()
        assert warranty.status == Warranty.WarrantyStatus.CLAIMED

    def test_file_claim_on_expired_raises(self, db, org, user, warranty):
        from apps.service.models import Warranty
        from apps.service.services import WarrantyService

        warranty.status = Warranty.WarrantyStatus.EXPIRED
        warranty.save()

        with tenant_context(org):
            with pytest.raises(ValueError, match="expired"):
                WarrantyService.file_claim(warranty, "claim on expired")

    def test_resolve_claim(self, db, org, user, warranty):
        from apps.service.models import WarrantyClaim
        from apps.service.services import WarrantyService

        with tenant_context(org):
            claim = WarrantyService.file_claim(warranty, "dripping faucet", user=user)
            resolved = WarrantyService.resolve_claim(
                claim, resolution="Repaired faucet", cost=Decimal("120.00")
            )

        assert resolved.status == WarrantyClaim.ClaimStatus.RESOLVED
        assert resolved.cost == Decimal("120.00")

    def test_expire_old_warranties(self, db, org, user, project):
        from apps.service.models import Warranty
        from apps.service.services import WarrantyService

        with tenant_context(org):
            old = Warranty.objects.create(
                organization=org, created_by=user, project=project,
                warranty_type=Warranty.WarrantyType.WORKMANSHIP,
                description="expired",
                coverage_details="x",
                start_date=date.today() - timedelta(days=400),
                end_date=date.today() - timedelta(days=1),
                status=Warranty.WarrantyStatus.ACTIVE,
            )

        count = WarrantyService.expire_old_warranties(organization=org)
        assert count == 1
        old.refresh_from_db()
        assert old.status == Warranty.WarrantyStatus.EXPIRED

    def test_get_expiring_soon(self, db, org, user, project):
        from apps.service.models import Warranty
        from apps.service.services import WarrantyService

        with tenant_context(org):
            soon = Warranty.objects.create(
                organization=org, created_by=user, project=project,
                warranty_type=Warranty.WarrantyType.MANUFACTURER,
                description="expiring soon",
                coverage_details="x",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=15),
                status=Warranty.WarrantyStatus.ACTIVE,
            )

        qs = WarrantyService.get_expiring_soon(org, days_ahead=30)
        assert soon in qs


# ---------------------------------------------------------------------------
# ServiceAgreement tests
# ---------------------------------------------------------------------------

class TestServiceAgreementModel:
    def test_visits_remaining(self, agreement):
        assert agreement.visits_remaining == 12

    def test_visits_remaining_after_visits(self, agreement):
        agreement.visits_completed = 5
        assert agreement.visits_remaining == 7

    def test_visits_remaining_never_negative(self, agreement):
        agreement.visits_completed = 20
        assert agreement.visits_remaining == 0


class TestServiceAgreementService:
    def test_record_visit(self, db, org, agreement):
        from apps.service.services import ServiceAgreementService

        with tenant_context(org):
            updated = ServiceAgreementService.record_visit(agreement)

        assert updated.visits_completed == 1

    def test_record_visit_increments(self, db, org, agreement):
        from apps.service.services import ServiceAgreementService

        with tenant_context(org):
            ServiceAgreementService.record_visit(agreement)
            updated = ServiceAgreementService.record_visit(agreement)

        assert updated.visits_completed == 2

    def test_renew_monthly_agreement(self, db, org, agreement):
        from apps.service.models import ServiceAgreement
        from apps.service.services import ServiceAgreementService

        original_end = agreement.end_date
        with tenant_context(org):
            renewed = ServiceAgreementService.renew_agreement(agreement)

        assert renewed.end_date > original_end
        assert renewed.visits_completed == 0
        assert renewed.status == ServiceAgreement.AgreementStatus.ACTIVE

    def test_expire_old_agreements(self, db, org, user, contact):
        from apps.service.models import ServiceAgreement
        from apps.service.services import ServiceAgreementService

        with tenant_context(org):
            old = ServiceAgreement.objects.create(
                organization=org, created_by=user,
                client=contact,
                name="Old Agreement",
                agreement_type=ServiceAgreement.AgreementType.INSPECTION,
                start_date=date.today() - timedelta(days=400),
                end_date=date.today() - timedelta(days=1),
                billing_frequency=ServiceAgreement.BillingFrequency.ANNUAL,
                billing_amount=Decimal("500.00"),
                visits_per_year=1,
                status=ServiceAgreement.AgreementStatus.ACTIVE,
            )

        count = ServiceAgreementService.expire_old_agreements(organization=org)
        assert count == 1
        old.refresh_from_db()
        assert old.status == ServiceAgreement.AgreementStatus.EXPIRED
