"""Tests for Analytics & Reporting Engine (Section 16)."""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.models import User
from apps.tenants.models import Organization
from apps.tenants.context import tenant_context


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="analytics_test@example.com",
        password="pass1234!",
        first_name="Analytics",
        last_name="Tester",
    )


@pytest.fixture
def org(db, user):
    return Organization.objects.create(
        name="Analytics Test Co",
        slug="analytics-test-co",
        owner=user,
    )


@pytest.fixture
def contact(db, org, user):
    from apps.crm.models import Contact
    with tenant_context(org):
        return Contact.objects.create(
            organization=org,
            created_by=user,
            first_name="Test",
            last_name="Client",
            email="testclient@example.com",
        )


@pytest.fixture
def project(db, org, user, contact):
    from apps.projects.models import Project
    with tenant_context(org):
        return Project.objects.create(
            organization=org,
            created_by=user,
            name="Analytics Project",
            status="production",
            client=contact,
            health_status="green",
        )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class TestDashboardModel:
    def test_create_dashboard(self, db, org, user):
        from apps.analytics.models import Dashboard
        with tenant_context(org):
            d = Dashboard.objects.create(
                organization=org,
                created_by=user,
                name="My Dashboard",
                layout={"cols": 3},
                widget_config={"show_kpis": True},
            )
        assert str(d) == "My Dashboard"
        assert d.is_default is False

    def test_set_default_unsets_others(self, db, org, user):
        from apps.analytics.models import Dashboard
        with tenant_context(org):
            d1 = Dashboard.objects.create(
                organization=org, created_by=user, name="D1", is_default=True
            )
            d2 = Dashboard.objects.create(
                organization=org, created_by=user, name="D2", is_default=False
            )
            # Simulate set_default logic
            Dashboard.objects.filter(
                organization=org, is_default=True
            ).exclude(pk=d2.pk).update(is_default=False)
            d2.is_default = True
            d2.save()

        d1.refresh_from_db()
        d2.refresh_from_db()
        assert d1.is_default is False
        assert d2.is_default is True


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

class TestReportModel:
    def test_create_report(self, db, org, user):
        from apps.analytics.models import Report
        with tenant_context(org):
            r = Report.objects.create(
                organization=org,
                created_by=user,
                name="Monthly Financial Report",
                report_type=Report.ReportType.FINANCIAL,
                query_config={"months": 1},
                is_active=True,
            )
        assert str(r) == "Monthly Financial Report"
        assert r.last_run_at is None
        assert r.last_run_result is None

    def test_report_types_include_service(self, db, org, user):
        from apps.analytics.models import Report
        types = [c[0] for c in Report.ReportType.choices]
        assert "service" in types
        assert "financial" in types
        assert "labor" in types
        assert "safety" in types


class TestReportService:
    def test_run_project_report(self, db, org, user, project):
        from apps.analytics.models import Report
        from apps.analytics.services import ReportService

        with tenant_context(org):
            report = Report.objects.create(
                organization=org,
                created_by=user,
                name="Project Status",
                report_type=Report.ReportType.PROJECT,
            )
            result = ReportService.run_report(report)

        assert result["report_type"] == "project"
        assert "total" in result
        assert result["total"] >= 1
        report.refresh_from_db()
        assert report.last_run_at is not None
        assert report.last_run_result is not None

    def test_run_financial_report(self, db, org, user):
        from apps.analytics.models import Report
        from apps.analytics.services import ReportService

        with tenant_context(org):
            report = Report.objects.create(
                organization=org,
                created_by=user,
                name="Financial Q",
                report_type=Report.ReportType.FINANCIAL,
                query_config={"months": 1},
            )
            result = ReportService.run_report(report)

        assert result["report_type"] == "financial"
        assert "period" in result

    def test_run_service_report(self, db, org, user):
        from apps.analytics.models import Report
        from apps.analytics.services import ReportService

        with tenant_context(org):
            report = Report.objects.create(
                organization=org,
                created_by=user,
                name="Service Summary",
                report_type=Report.ReportType.SERVICE,
            )
            result = ReportService.run_report(report)

        assert result["report_type"] == "service"
        assert "active_warranties" in result

    def test_run_safety_report(self, db, org, user, project):
        from apps.analytics.models import Report
        from apps.analytics.services import ReportService

        with tenant_context(org):
            report = Report.objects.create(
                organization=org,
                created_by=user,
                name="Safety Report",
                report_type=Report.ReportType.SAFETY,
                query_config={"months": 1},
            )
            result = ReportService.run_report(report)

        assert result["report_type"] == "safety"
        assert "incidents_by_type" in result

    def test_run_labor_report(self, db, org, user, project):
        from apps.analytics.models import Report
        from apps.analytics.services import ReportService

        with tenant_context(org):
            report = Report.objects.create(
                organization=org,
                created_by=user,
                name="Labor Report",
                report_type=Report.ReportType.LABOR,
                query_config={"months": 1},
            )
            result = ReportService.run_report(report)

        assert result["report_type"] == "labor"
        assert "labor_by_project" in result


# ---------------------------------------------------------------------------
# KPI
# ---------------------------------------------------------------------------

class TestKPIModel:
    def test_create_kpi(self, db, org, user):
        from apps.analytics.models import KPI
        today = date.today()
        with tenant_context(org):
            k = KPI.objects.create(
                organization=org,
                created_by=user,
                name="Revenue MTD",
                category=KPI.Category.FINANCIAL,
                value=Decimal("150000.00"),
                target=Decimal("120000.00"),
                unit="USD",
                period_start=today.replace(day=1),
                period_end=today,
            )
        assert k.is_on_target is True
        assert "Revenue MTD" in str(k)

    def test_is_on_target_false(self, db, org, user):
        from apps.analytics.models import KPI
        today = date.today()
        with tenant_context(org):
            k = KPI.objects.create(
                organization=org,
                created_by=user,
                name="Revenue MTD",
                category=KPI.Category.FINANCIAL,
                value=Decimal("5"),
                target=Decimal("10"),
                unit="USD",
                period_start=today.replace(day=1),
                period_end=today,
            )
        assert k.is_on_target is False

    def test_is_on_target_none_when_no_target(self, db, org, user):
        from apps.analytics.models import KPI
        today = date.today()
        with tenant_context(org):
            k = KPI.objects.create(
                organization=org,
                created_by=user,
                name="Active Projects",
                category=KPI.Category.PROJECT,
                value=Decimal("5"),
                target=None,
                unit="count",
                period_start=today.replace(day=1),
                period_end=today,
            )
        assert k.is_on_target is None

    def test_trend_default_stable(self, db, org, user):
        from apps.analytics.models import KPI
        today = date.today()
        with tenant_context(org):
            k = KPI.objects.create(
                organization=org, created_by=user,
                name="Test KPI", category=KPI.Category.PROJECT,
                value=Decimal("10"), unit="count",
                period_start=today.replace(day=1), period_end=today,
            )
        assert k.trend == KPI.Trend.STABLE


class TestKPIService:
    def test_calculate_all_kpis_returns_list(self, db, org, user, project):
        from apps.analytics.services import KPIService

        with tenant_context(org):
            results = KPIService.calculate_all_kpis(org)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_calculate_kpis_upserts(self, db, org, user, project):
        """Running twice should not duplicate KPIs."""
        from apps.analytics.models import KPI
        from apps.analytics.services import KPIService

        with tenant_context(org):
            r1 = KPIService.calculate_all_kpis(org)
            count1 = KPI.objects.filter(organization=org).count()
            r2 = KPIService.calculate_all_kpis(org)
            count2 = KPI.objects.filter(organization=org).count()

        assert count1 == count2  # no duplicates

    def test_get_org_summary_structure(self, db, org, user, project):
        from apps.analytics.services import KPIService

        with tenant_context(org):
            summary = KPIService.get_org_summary(org)

        assert "financial" in summary
        assert "projects" in summary
        assert "labor" in summary
        assert "safety" in summary
        assert "service" in summary

    def test_project_summary_counts(self, db, org, user, project):
        from apps.analytics.services import KPIService

        with tenant_context(org):
            summary = KPIService.get_org_summary(org)

        projects = summary["projects"]
        assert projects["total_projects"] >= 1
        assert projects["active_projects"] >= 1


# ---------------------------------------------------------------------------
# ExportService
# ---------------------------------------------------------------------------

class TestExportService:
    def test_export_kpis_csv(self, db, org, user, project):
        from apps.analytics.services import ExportService, KPIService

        with tenant_context(org):
            KPIService.calculate_all_kpis(org)
            csv_bytes = ExportService.export_kpis_to_csv(org)

        assert csv_bytes
        decoded = csv_bytes.decode("utf-8")
        assert "name" in decoded
        assert "category" in decoded
        assert "value" in decoded

    def test_export_report_result_csv(self, db, org, user):
        from apps.analytics.models import Report
        from apps.analytics.services import ExportService, ReportService

        with tenant_context(org):
            report = Report.objects.create(
                organization=org, created_by=user,
                name="Export Test", report_type=Report.ReportType.PROJECT,
            )
            ReportService.run_report(report)
            csv_bytes = ExportService.export_report_result_to_csv(report)

        # May be empty if no list data, but should not raise
        assert isinstance(csv_bytes, bytes)

    def test_export_empty_report_returns_empty(self, db, org, user):
        from apps.analytics.models import Report
        from apps.analytics.services import ExportService

        with tenant_context(org):
            report = Report.objects.create(
                organization=org, created_by=user,
                name="No Data", report_type=Report.ReportType.PROJECT,
            )
            csv_bytes = ExportService.export_report_result_to_csv(report)

        assert csv_bytes == b""
