"""Section 14: Payroll & Workforce Management tests."""
import pytest
from datetime import date, timedelta
from decimal import Decimal


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def org_and_user(db):
    """Create an org and an OWNER user."""
    from django.contrib.auth import get_user_model
    from apps.tenants.models import Organization

    User = get_user_model()
    user = User.objects.create_user(
        email="payroll@test.com",
        password="test1234!",
        first_name="Payroll",
        last_name="Admin",
    )
    org = Organization.objects.create(
        name="Payroll Test Org",
        slug="payroll-test-org",
        subscription_status="active",
        owner=user,
    )
    return org, user


@pytest.fixture
def project(db, org_and_user):
    """Create a test project."""
    from apps.projects.models import Project
    from apps.tenants.context import tenant_context

    org, user = org_and_user
    with tenant_context(org):
        return Project.objects.create(
            organization=org,
            name="Payroll Test Project",
            project_number="BSP-2026-099",
            status="production",
        )


@pytest.fixture
def employee(db, org_and_user):
    """Create a test employee."""
    from apps.payroll.models import Employee
    from apps.tenants.context import tenant_context

    org, user = org_and_user
    with tenant_context(org):
        return Employee.objects.create(
            organization=org,
            employee_id="EMP-001",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            employment_type="w2_full_time",
            trade="general",
            hire_date=date(2023, 1, 1),
            base_hourly_rate=Decimal("25.00"),
            overtime_rate_multiplier=Decimal("1.50"),
            burden_rate=Decimal("0.2800"),
        )


@pytest.fixture
def payroll_run(db, org_and_user):
    """Create a test payroll run."""
    from apps.payroll.models import PayrollRun
    from apps.tenants.context import tenant_context

    org, user = org_and_user
    with tenant_context(org):
        return PayrollRun.objects.create(
            organization=org,
            pay_period_start=date(2026, 2, 1),
            pay_period_end=date(2026, 2, 14),
            run_date=date(2026, 2, 15),
            check_date=date(2026, 2, 18),
        )


# ---------------------------------------------------------------------------
# PayrollCalculationService
# ---------------------------------------------------------------------------

class TestPayrollCalculationService:

    def test_calculate_entry_regular_only(self, db, employee):
        """Regular-only pay calculation."""
        from apps.payroll.services import PayrollCalculationService

        result = PayrollCalculationService.calculate_entry(
            employee,
            regular_hours=Decimal("40"),
        )
        expected_gross = Decimal("40") * Decimal("25.00")  # 1000.00
        assert result["gross_pay"] == expected_gross
        assert result["regular_hours"] == Decimal("40")
        assert result["overtime_hours"] == Decimal("0")
        assert result["net_pay"] < result["gross_pay"]

    def test_calculate_entry_with_overtime(self, db, employee):
        """Overtime hours should apply 1.5x multiplier."""
        from apps.payroll.services import PayrollCalculationService

        result = PayrollCalculationService.calculate_entry(
            employee,
            regular_hours=Decimal("40"),
            overtime_hours=Decimal("8"),
        )
        ot_pay = Decimal("8") * Decimal("25.00") * Decimal("1.50")  # 300.00
        regular_pay = Decimal("40") * Decimal("25.00")  # 1000.00
        expected_gross = regular_pay + ot_pay
        assert result["gross_pay"] == expected_gross

    def test_calculate_entry_with_double_time(self, db, employee):
        """Double-time hours should apply 2.0x multiplier."""
        from apps.payroll.services import PayrollCalculationService

        result = PayrollCalculationService.calculate_entry(
            employee,
            regular_hours=Decimal("40"),
            double_time_hours=Decimal("4"),
        )
        dt_pay = Decimal("4") * Decimal("25.00") * Decimal("2.00")  # 200.00
        regular_pay = Decimal("40") * Decimal("25.00")  # 1000.00
        expected_gross = regular_pay + dt_pay
        assert result["gross_pay"] == expected_gross

    def test_tax_components_present(self, db, employee):
        """All expected tax components are calculated."""
        from apps.payroll.services import PayrollCalculationService

        result = PayrollCalculationService.calculate_entry(
            employee, regular_hours=Decimal("40")
        )
        for key in ("federal_tax", "state_tax", "fica", "medicare", "net_pay"):
            assert key in result
            assert result[key] > Decimal("0")

    def test_net_pay_less_than_gross(self, db, employee):
        """Net pay must be less than gross pay after taxes."""
        from apps.payroll.services import PayrollCalculationService

        result = PayrollCalculationService.calculate_entry(
            employee, regular_hours=Decimal("40")
        )
        assert result["net_pay"] < result["gross_pay"]

    def test_approve_run(self, db, org_and_user, payroll_run):
        """Approving a DRAFT run sets status to APPROVED."""
        from apps.payroll.services import PayrollCalculationService
        from apps.payroll.models import PayrollRun

        org, user = org_and_user
        updated = PayrollCalculationService.approve_run(payroll_run, user)
        assert updated.status == PayrollRun.Status.APPROVED
        assert updated.approved_by == user
        assert updated.approved_at is not None

    def test_approve_run_wrong_status_raises(self, db, org_and_user, payroll_run):
        """Approving an already-approved run should raise ValueError."""
        from apps.payroll.services import PayrollCalculationService
        from apps.payroll.models import PayrollRun

        org, user = org_and_user
        payroll_run.status = PayrollRun.Status.PAID
        payroll_run.save(update_fields=["status"])
        with pytest.raises(ValueError):
            PayrollCalculationService.approve_run(payroll_run, user)

    def test_mark_paid(self, db, org_and_user, payroll_run):
        """Marking an APPROVED run as PAID works correctly."""
        from apps.payroll.services import PayrollCalculationService
        from apps.payroll.models import PayrollRun

        org, user = org_and_user
        PayrollCalculationService.approve_run(payroll_run, user)
        updated = PayrollCalculationService.mark_paid(payroll_run)
        assert updated.status == PayrollRun.Status.PAID

    def test_void_run(self, db, payroll_run):
        """Voiding a DRAFT run sets status to VOID."""
        from apps.payroll.services import PayrollCalculationService
        from apps.payroll.models import PayrollRun

        updated = PayrollCalculationService.void_run(payroll_run)
        assert updated.status == PayrollRun.Status.VOID

    def test_void_paid_run_raises(self, db, org_and_user, payroll_run):
        """Cannot void a PAID run."""
        from apps.payroll.services import PayrollCalculationService
        from apps.payroll.models import PayrollRun

        org, user = org_and_user
        PayrollCalculationService.approve_run(payroll_run, user)
        PayrollCalculationService.mark_paid(payroll_run)
        with pytest.raises(ValueError):
            PayrollCalculationService.void_run(payroll_run)

    def test_update_run_totals(self, db, org_and_user, employee, payroll_run):
        """_update_run_totals aggregates PayrollEntry totals onto the run."""
        from apps.payroll.services import PayrollCalculationService
        from apps.payroll.models import PayrollEntry

        calc = PayrollCalculationService.calculate_entry(employee, regular_hours=Decimal("40"))
        PayrollEntry.objects.create(payroll_run=payroll_run, employee=employee, **calc)
        PayrollCalculationService._update_run_totals(payroll_run)
        payroll_run.refresh_from_db()
        assert payroll_run.total_gross == calc["gross_pay"]
        assert payroll_run.total_net == calc["net_pay"]


# ---------------------------------------------------------------------------
# CertifiedPayrollService
# ---------------------------------------------------------------------------

class TestCertifiedPayrollService:

    def test_generate_report_no_entries(self, db, org_and_user, project, payroll_run):
        """Report generates with zero compliance issues when there are no entries."""
        from apps.payroll.services import CertifiedPayrollService
        from apps.payroll.models import CertifiedPayrollReport

        report = CertifiedPayrollService.generate_report(payroll_run, project)
        assert report.status == CertifiedPayrollReport.ReportStatus.DRAFT
        assert report.compliance_issues == []
        assert report.project == project
        assert report.payroll_run == payroll_run

    def test_generate_report_detects_wage_shortfall(
        self, db, org_and_user, project, payroll_run, employee
    ):
        """Compliance issue detected when paid rate < prevailing rate."""
        from apps.payroll.models import PayrollEntry, PrevailingWageRate
        from apps.payroll.services import CertifiedPayrollService
        from apps.tenants.context import tenant_context

        org, user = org_and_user
        with tenant_context(org):
            # Set a prevailing rate higher than employee's base rate
            PrevailingWageRate.objects.create(
                organization=org,
                project=project,
                trade="general",
                base_rate=Decimal("35.00"),  # higher than employee's $25/hr
                fringe_rate=Decimal("5.00"),
                effective_date=date(2026, 1, 1),
            )
            # Create a payroll entry with allocation to this project
            from apps.payroll.services import PayrollCalculationService
            calc = PayrollCalculationService.calculate_entry(
                employee, regular_hours=Decimal("40")
            )
            calc["job_cost_allocations"] = [
                {
                    "project_id": str(project.pk),
                    "cost_code_id": None,
                    "hours": 40.0,
                    "amount": float(Decimal("40") * employee.burdened_rate),
                }
            ]
            PayrollEntry.objects.create(payroll_run=payroll_run, employee=employee, **calc)

        report = CertifiedPayrollService.generate_report(payroll_run, project)
        assert len(report.compliance_issues) == 1
        issue = report.compliance_issues[0]
        assert issue["trade"] == "general"
        assert issue["paid_rate"] == float(employee.base_hourly_rate)
        assert issue["required_rate"] == 40.0  # base_rate + fringe_rate
        assert issue["shortfall"] > 0

    def test_submit_report(self, db, org_and_user, project, payroll_run):
        """DRAFT report can be submitted."""
        from apps.payroll.services import CertifiedPayrollService
        from apps.payroll.models import CertifiedPayrollReport

        report = CertifiedPayrollService.generate_report(payroll_run, project)
        updated = CertifiedPayrollService.submit_report(report)
        assert updated.status == CertifiedPayrollReport.ReportStatus.SUBMITTED

    def test_submit_non_draft_raises(self, db, org_and_user, project, payroll_run):
        """Submitting a non-DRAFT report raises ValueError."""
        from apps.payroll.services import CertifiedPayrollService
        from apps.payroll.models import CertifiedPayrollReport

        report = CertifiedPayrollService.generate_report(payroll_run, project)
        CertifiedPayrollService.submit_report(report)
        with pytest.raises(ValueError):
            CertifiedPayrollService.submit_report(report)


# ---------------------------------------------------------------------------
# WorkforceService
# ---------------------------------------------------------------------------

class TestWorkforceService:

    def test_update_certification_adds_new(self, db, org_and_user, employee):
        """Adding a new certification to an employee with no existing certs."""
        from apps.payroll.services import WorkforceService

        expiry = date(2027, 6, 1)
        updated = WorkforceService.update_certification(
            employee,
            cert_name="OSHA 30",
            cert_number="OS-12345",
            expiry=expiry,
            issuing_body="OSHA",
        )
        assert len(updated.certifications) == 1
        cert = updated.certifications[0]
        assert cert["name"] == "OSHA 30"
        assert cert["number"] == "OS-12345"
        assert cert["expiry"] == str(expiry)

    def test_update_certification_updates_existing(self, db, org_and_user, employee):
        """Updating an existing certification replaces the old entry."""
        from apps.payroll.services import WorkforceService

        employee.certifications = [
            {"name": "OSHA 30", "number": "OLD-001", "expiry": "2025-01-01", "issuing_body": "OSHA"}
        ]
        employee.save(update_fields=["certifications"])

        new_expiry = date(2028, 6, 1)
        updated = WorkforceService.update_certification(
            employee,
            cert_name="OSHA 30",
            cert_number="NEW-002",
            expiry=new_expiry,
        )
        assert len(updated.certifications) == 1
        assert updated.certifications[0]["number"] == "NEW-002"
        assert updated.certifications[0]["expiry"] == str(new_expiry)

    def test_get_expiring_certifications(self, db, org_and_user, employee):
        """Returns certifications expiring within 30 days."""
        from apps.payroll.services import WorkforceService
        from apps.tenants.context import tenant_context

        org, user = org_and_user
        expiry_soon = date.today() + timedelta(days=10)
        employee.certifications = [
            {"name": "First Aid", "number": "FA-001", "expiry": str(expiry_soon), "issuing_body": "Red Cross"},
        ]
        employee.save(update_fields=["certifications"])

        with tenant_context(org):
            expiring = WorkforceService.get_expiring_certifications(org, days_ahead=30)

        assert len(expiring) == 1
        assert expiring[0]["cert_name"] == "First Aid"
        assert expiring[0]["days_until_expiry"] == 10

    def test_get_expiring_certifications_excludes_future(self, db, org_and_user, employee):
        """Certifications expiring far in the future should not appear."""
        from apps.payroll.services import WorkforceService

        org, user = org_and_user
        far_future = date.today() + timedelta(days=365)
        employee.certifications = [
            {"name": "CPR", "number": "C-001", "expiry": str(far_future), "issuing_body": "AHA"},
        ]
        employee.save(update_fields=["certifications"])

        expiring = WorkforceService.get_expiring_certifications(org, days_ahead=30)
        assert len(expiring) == 0

    def test_terminate_employee(self, db, employee):
        """Terminating employee sets is_active=False and termination_date."""
        from apps.payroll.services import WorkforceService

        updated = WorkforceService.terminate_employee(employee, date(2026, 2, 28))
        assert updated.is_active is False
        assert updated.termination_date == date(2026, 2, 28)

    def test_terminate_employee_uses_today_as_default(self, db, employee):
        """Terminating without date defaults to today."""
        from apps.payroll.services import WorkforceService

        updated = WorkforceService.terminate_employee(employee)
        assert updated.is_active is False
        assert updated.termination_date == date.today()

    def test_get_skills_inventory(self, db, org_and_user, employee):
        """Skills inventory counts employees by trade and type."""
        from apps.payroll.services import WorkforceService
        from apps.tenants.context import tenant_context

        org, user = org_and_user
        with tenant_context(org):
            inventory = WorkforceService.get_skills_inventory(org)

        assert inventory["total_active"] >= 1
        assert "general" in inventory["by_trade"]
        assert "w2_full_time" in inventory["by_employment_type"]


# ---------------------------------------------------------------------------
# Employee model properties
# ---------------------------------------------------------------------------

class TestEmployeeModel:

    def test_full_name(self, db, employee):
        assert employee.full_name == "John Doe"

    def test_burdened_rate(self, db, employee):
        """Burdened rate = base_hourly_rate * (1 + burden_rate)."""
        expected = Decimal("25.00") * (Decimal("1") + Decimal("0.2800"))
        assert employee.burdened_rate == expected.quantize(Decimal("0.01"))

    def test_prevailing_wage_total_rate_auto_calc(self, db, org_and_user, project):
        """PrevailingWageRate.total_rate is auto-calculated on save."""
        from apps.payroll.models import PrevailingWageRate
        from apps.tenants.context import tenant_context

        org, user = org_and_user
        with tenant_context(org):
            rate = PrevailingWageRate.objects.create(
                organization=org,
                project=project,
                trade="electrical",
                base_rate=Decimal("45.00"),
                fringe_rate=Decimal("8.50"),
                effective_date=date(2026, 1, 1),
            )
        assert rate.total_rate == Decimal("53.50")
