"""Section 12: Field Operations Hub tests."""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone as django_tz


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def org_and_user(db):
    """Create an org and a user with OWNER membership."""
    from apps.tenants.models import Organization, OrganizationMembership
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(
        email="field@test.com",
        password="test1234!",
        first_name="Field",
        last_name="Worker",
    )
    org = Organization.objects.create(
        name="Test Org",
        slug="test-org-field",
        subscription_status="active",
        owner=user,
    )
    # Signal auto-creates OWNER membership; no need to create manually
    return org, user


@pytest.fixture
def project(db, org_and_user):
    """Create a project."""
    from apps.projects.models import Project
    from apps.tenants.context import tenant_context

    org, user = org_and_user
    with tenant_context(org):
        return Project.objects.create(
            organization=org,
            name="Test Project",
            project_number="BSP-2026-099",
            status="production",
        )


# ---------------------------------------------------------------------------
# TimeClockService tests
# ---------------------------------------------------------------------------

class TestTimeClockService:

    def test_clock_in_creates_entry(self, db, org_and_user, project):
        """Clock in creates a new open TimeEntry."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.services import TimeClockService

        org, user = org_and_user
        with tenant_context(org):
            entry, created = TimeClockService.clock_in(
                user=user, project=project, organization=org,
            )

        assert created is True
        assert entry.clock_in is not None
        assert entry.clock_out is None
        assert entry.hours == Decimal("0.00")

    def test_clock_in_idempotent(self, db, org_and_user, project):
        """Calling clock_in when already clocked in returns existing entry."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.services import TimeClockService

        org, user = org_and_user
        with tenant_context(org):
            entry1, created1 = TimeClockService.clock_in(user=user, project=project, organization=org)
            entry2, created2 = TimeClockService.clock_in(user=user, project=project, organization=org)

        assert created2 is False
        assert entry1.pk == entry2.pk

    def test_clock_out_calculates_hours(self, db, org_and_user, project):
        """Clock out computes correct hours."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import TimeEntry
        from apps.field_ops.services import TimeClockService

        org, user = org_and_user
        with tenant_context(org):
            entry, _ = TimeClockService.clock_in(user=user, project=project, organization=org)

        # Manually set clock_in to 8 hours ago
        eight_hours_ago = django_tz.now() - timedelta(hours=8)
        TimeEntry.objects.filter(pk=entry.pk).update(clock_in=eight_hours_ago)
        entry.refresh_from_db()

        with tenant_context(org):
            entry = TimeClockService.clock_out(entry)

        assert entry.hours == pytest.approx(Decimal("8.00"), abs=Decimal("0.05"))
        assert entry.clock_out is not None

    def test_daily_overtime_calculated_on_clock_out(self, db, org_and_user, project):
        """Entries over 8h get overtime_hours set."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import TimeEntry
        from apps.field_ops.services import TimeClockService

        org, user = org_and_user
        with tenant_context(org):
            entry, _ = TimeClockService.clock_in(user=user, project=project, organization=org)

        # 10 hours ago
        TimeEntry.objects.filter(pk=entry.pk).update(
            clock_in=django_tz.now() - timedelta(hours=10)
        )
        entry.refresh_from_db()

        with tenant_context(org):
            entry = TimeClockService.clock_out(entry)

        assert entry.hours > Decimal("8.00")
        assert entry.overtime_hours > Decimal("0.00")

    def test_manual_entry_creation(self, db, org_and_user, project):
        """Manual time entries are created with correct hours and no clock_in/out."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.services import TimeClockService

        org, user = org_and_user
        with tenant_context(org):
            entry = TimeClockService.create_manual_entry(
                user=user,
                project=project,
                organization=org,
                entry_date=date.today(),
                hours=Decimal("6.50"),
            )

        assert entry.clock_in is None
        assert entry.clock_out is None
        assert entry.hours == Decimal("6.50")
        assert entry.overtime_hours == Decimal("0.00")

    def test_weekly_overtime_calculation(self, db, org_and_user, project):
        """Weekly overtime kicks in after 40 hours."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import TimeEntry
        from apps.field_ops.services import TimeClockService

        org, user = org_and_user
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Create 5 days × 9 hours = 45 hours total (5 OT)
        with tenant_context(org):
            for i in range(5):
                TimeEntry.objects.create(
                    organization=org,
                    user=user,
                    project=project,
                    date=week_start + timedelta(days=i),
                    hours=Decimal("9.00"),
                    overtime_hours=Decimal("1.00"),  # daily OT
                    entry_type="manual",
                    status="pending",
                )
            updated = TimeClockService.calculate_weekly_overtime(user, org, week_start)

        # After 40 hours, 5 hours are weekly OT — some entries should have updated OT
        total_ot = sum(
            TimeEntry.objects.filter(
                organization=org, user=user, date__gte=week_start
            ).values_list("overtime_hours", flat=True)
        )
        assert total_ot >= Decimal("5.00")


# ---------------------------------------------------------------------------
# DailyLogService tests
# ---------------------------------------------------------------------------

class TestDailyLogService:

    def test_create_log_draft(self, db, org_and_user, project):
        """Creating a log creates a DRAFT status entry."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import DailyLog
        from apps.field_ops.services import DailyLogService

        org, user = org_and_user
        with tenant_context(org):
            log, created = DailyLogService.get_or_create_log(
                project=project,
                log_date=date.today(),
                user=user,
                organization=org,
            )

        assert created is True
        assert log.status == DailyLog.Status.DRAFT

    def test_submit_log(self, db, org_and_user, project):
        """Submitting a draft log transitions to SUBMITTED."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import DailyLog
        from apps.field_ops.services import DailyLogService

        org, user = org_and_user
        with tenant_context(org):
            log, _ = DailyLogService.get_or_create_log(
                project=project, log_date=date.today(), user=user, organization=org,
            )
            log = DailyLogService.submit_log(log, user)

        assert log.status == DailyLog.Status.SUBMITTED
        assert log.submitted_by == user

    def test_approve_log(self, db, org_and_user, project):
        """Approving a submitted log transitions to APPROVED."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import DailyLog
        from apps.field_ops.services import DailyLogService

        org, user = org_and_user
        with tenant_context(org):
            log, _ = DailyLogService.get_or_create_log(
                project=project, log_date=date.today(), user=user, organization=org,
            )
            DailyLogService.submit_log(log, user)
            log.refresh_from_db()
            log = DailyLogService.approve_log(log, approver=user)

        assert log.status == DailyLog.Status.APPROVED
        assert log.approved_by == user
        assert log.approved_at is not None

    def test_cannot_submit_approved_log(self, db, org_and_user, project):
        """Cannot submit a log that's already approved."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.services import DailyLogService

        org, user = org_and_user
        with tenant_context(org):
            log, _ = DailyLogService.get_or_create_log(
                project=project, log_date=date.today(), user=user, organization=org,
            )
            DailyLogService.submit_log(log, user)
            log.refresh_from_db()
            DailyLogService.approve_log(log, approver=user)
            log.refresh_from_db()

            with pytest.raises(ValueError):
                DailyLogService.submit_log(log, user)

    def test_unique_log_per_project_per_day(self, db, org_and_user, project):
        """Only one log per project per date."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.services import DailyLogService

        org, user = org_and_user
        with tenant_context(org):
            log1, created1 = DailyLogService.get_or_create_log(
                project=project, log_date=date.today(), user=user, organization=org,
            )
            log2, created2 = DailyLogService.get_or_create_log(
                project=project, log_date=date.today(), user=user, organization=org,
            )

        assert created1 is True
        assert created2 is False
        assert log1.pk == log2.pk

    def test_calendar_data(self, db, org_and_user, project):
        """Calendar data returns dict keyed by date."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.services import DailyLogService

        org, user = org_and_user
        today = date.today()
        with tenant_context(org):
            log, _ = DailyLogService.get_or_create_log(
                project=project, log_date=today, user=user, organization=org,
            )
            calendar = DailyLogService.get_calendar_data(
                project=project, organization=org, year=today.year, month=today.month,
            )

        assert str(today) in calendar
        assert calendar[str(today)]["status"] == "draft"


# ---------------------------------------------------------------------------
# BulkApprovalService tests
# ---------------------------------------------------------------------------

class TestBulkApprovalService:

    def test_bulk_approve_time_entries(self, db, org_and_user, project):
        """Bulk approve updates status and sets approver."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import TimeEntry
        from apps.field_ops.services import BulkApprovalService

        org, user = org_and_user
        with tenant_context(org):
            entries = [
                TimeEntry.objects.create(
                    organization=org, user=user, project=project,
                    date=date.today(), hours=Decimal("8.00"),
                    entry_type="manual", status="pending",
                )
                for _ in range(3)
            ]
            ids = [e.pk for e in entries]
            count = BulkApprovalService.bulk_approve_time_entries(ids, user, org)

        assert count == 3
        for entry in TimeEntry.objects.filter(pk__in=ids):
            assert entry.status == "approved"
            assert entry.approved_by == user

    def test_bulk_approve_expenses(self, db, org_and_user, project):
        """Bulk approve expenses sets status to APPROVED."""
        from apps.tenants.context import tenant_context
        from apps.field_ops.models import ExpenseEntry
        from apps.field_ops.services import BulkApprovalService

        org, user = org_and_user
        with tenant_context(org):
            expenses = [
                ExpenseEntry.objects.create(
                    organization=org, user=user, project=project,
                    date=date.today(), category="fuel",
                    description=f"Gas {i}", amount=Decimal("50.00"),
                    status="pending",
                )
                for i in range(2)
            ]
            ids = [e.pk for e in expenses]
            count = BulkApprovalService.bulk_approve_expenses(ids, user, org)

        assert count == 2
        for expense in ExpenseEntry.objects.filter(pk__in=ids):
            assert expense.status == "approved"

    def test_geofence_check(self, db):
        """Haversine geofence check returns correct result."""
        from apps.field_ops.services import TimeClockService

        # Center: San Francisco
        center = {"lat": 37.7749, "lng": -122.4194}

        # Same point — within radius
        assert TimeClockService._check_geofence(
            {"lat": 37.7749, "lng": -122.4194}, center, 100
        ) is True

        # ~50km away (San Jose) — outside 100m radius
        assert TimeClockService._check_geofence(
            {"lat": 37.3382, "lng": -121.8863}, center, 100
        ) is False
