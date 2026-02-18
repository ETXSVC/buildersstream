"""Section 13: Quality & Safety tests."""
import pytest
from datetime import date


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def org_and_user(db):
    """Create an org and a user with OWNER membership."""
    from django.contrib.auth import get_user_model

    from apps.tenants.models import Organization

    User = get_user_model()
    user = User.objects.create_user(
        email="qs@test.com",
        password="test1234!",
        first_name="QS",
        last_name="Tester",
    )
    org = Organization.objects.create(
        name="QS Test Org",
        slug="qs-test-org",
        subscription_status="active",
        owner=user,
    )
    return org, user


@pytest.fixture
def project(db, org_and_user):
    from apps.projects.models import Project
    from apps.tenants.context import tenant_context

    org, user = org_and_user
    with tenant_context(org):
        return Project.objects.create(
            organization=org,
            name="QS Project",
            project_number="BSP-2026-013",
            status="production",
        )


@pytest.fixture
def checklist(db, org_and_user):
    """Create an InspectionChecklist with 3 items."""
    from apps.quality_safety.models import ChecklistItem, InspectionChecklist
    from apps.tenants.context import tenant_context

    org, _ = org_and_user
    with tenant_context(org):
        cl = InspectionChecklist.objects.create(
            organization=org,
            name="Test Framing Checklist",
            checklist_type=InspectionChecklist.ChecklistType.QUALITY,
            category=InspectionChecklist.Category.FRAMING,
            is_template=True,
        )
        ChecklistItem.objects.bulk_create([
            ChecklistItem(checklist=cl, description="Item A", sort_order=0, is_required=True),
            ChecklistItem(checklist=cl, description="Item B", sort_order=1, is_required=True),
            ChecklistItem(checklist=cl, description="Item C", sort_order=2, is_required=False),
        ])
    return cl


# ---------------------------------------------------------------------------
# InspectionService tests
# ---------------------------------------------------------------------------

class TestInspectionService:

    def test_create_from_checklist_seeds_results(self, db, org_and_user, project, checklist):
        """create_from_checklist creates Inspection + InspectionResult rows."""
        from apps.quality_safety.models import Inspection, InspectionResult
        from apps.quality_safety.services import InspectionService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            inspection = InspectionService.create_from_checklist(
                checklist=checklist,
                project=project,
                organization=org,
                inspection_date=date.today(),
            )

        assert inspection.pk is not None
        assert inspection.status == Inspection.Status.SCHEDULED
        result_count = InspectionResult.objects.filter(inspection=inspection).count()
        assert result_count == 3

    def test_calculate_score_all_pass(self, db, org_and_user, project, checklist):
        """100% pass → score = 100."""
        from apps.quality_safety.models import InspectionResult
        from apps.quality_safety.services import InspectionService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            inspection = InspectionService.create_from_checklist(
                checklist=checklist, project=project, organization=org,
            )
            InspectionResult.objects.filter(inspection=inspection).update(
                status=InspectionResult.Status.PASS
            )
            score = InspectionService.calculate_score(inspection)

        assert score == 100

    def test_calculate_score_partial(self, db, org_and_user, project, checklist):
        """2 pass, 1 fail → score = 67."""
        from apps.quality_safety.models import InspectionResult
        from apps.quality_safety.services import InspectionService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            inspection = InspectionService.create_from_checklist(
                checklist=checklist, project=project, organization=org,
            )
            results = list(InspectionResult.objects.filter(inspection=inspection))
            results[0].status = InspectionResult.Status.PASS
            results[1].status = InspectionResult.Status.PASS
            results[2].status = InspectionResult.Status.FAIL
            InspectionResult.objects.bulk_update(results, ["status"])
            score = InspectionService.calculate_score(inspection)

        assert score == 67

    def test_calculate_score_all_na(self, db, org_and_user, project, checklist):
        """All N/A → score = None (no inspectable items)."""
        from apps.quality_safety.models import InspectionResult
        from apps.quality_safety.services import InspectionService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            inspection = InspectionService.create_from_checklist(
                checklist=checklist, project=project, organization=org,
            )
            InspectionResult.objects.filter(inspection=inspection).update(
                status=InspectionResult.Status.NA
            )
            score = InspectionService.calculate_score(inspection)

        assert score is None

    def test_record_results_updates_score(self, db, org_and_user, project, checklist):
        """record_results bulk-updates results and recalculates score."""
        from apps.quality_safety.models import Inspection, InspectionResult
        from apps.quality_safety.services import InspectionService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            inspection = InspectionService.create_from_checklist(
                checklist=checklist, project=project, organization=org,
            )
            results = list(InspectionResult.objects.filter(inspection=inspection))
            results_data = [
                {"checklist_item_id": str(r.checklist_item_id), "status": "pass"}
                for r in results
            ]
            inspection = InspectionService.record_results(inspection, results_data)

        assert inspection.status == Inspection.Status.IN_PROGRESS
        assert inspection.overall_score == 100

    def test_complete_inspection_validates_status(self, db, org_and_user, project, checklist):
        """complete_inspection raises ValueError for invalid final status."""
        from apps.quality_safety.services import InspectionService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            inspection = InspectionService.create_from_checklist(
                checklist=checklist, project=project, organization=org,
            )
            with pytest.raises(ValueError):
                InspectionService.complete_inspection(inspection, "scheduled")

    def test_complete_inspection_passed(self, db, org_and_user, project, checklist):
        """complete_inspection sets PASSED status."""
        from apps.quality_safety.models import Inspection
        from apps.quality_safety.services import InspectionService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            inspection = InspectionService.create_from_checklist(
                checklist=checklist, project=project, organization=org,
            )
            inspection = InspectionService.complete_inspection(
                inspection, Inspection.Status.PASSED, overall_score=95, notes="Looks good."
            )

        assert inspection.status == Inspection.Status.PASSED
        assert inspection.overall_score == 95
        assert inspection.notes == "Looks good."


# ---------------------------------------------------------------------------
# DeficiencyService tests
# ---------------------------------------------------------------------------

class TestDeficiencyService:

    def _make_deficiency(self, org, project, severity="minor", status="open"):
        from apps.quality_safety.models import Deficiency
        from apps.tenants.context import tenant_context

        with tenant_context(org):
            return Deficiency.objects.create(
                organization=org,
                project=project,
                title="Test Deficiency",
                description="Something is wrong",
                severity=severity,
                status=status,
            )

    def test_resolve_transitions_to_resolved(self, db, org_and_user, project):
        from apps.quality_safety.models import Deficiency
        from apps.quality_safety.services import DeficiencyService

        org, user = org_and_user
        deficiency = self._make_deficiency(org, project)
        deficiency = DeficiencyService.resolve(deficiency, notes="Fixed.", resolved_by=user)

        assert deficiency.status == Deficiency.Status.RESOLVED
        assert deficiency.resolved_by == user
        assert deficiency.resolved_date == date.today()

    def test_resolve_rejects_already_resolved(self, db, org_and_user, project):
        from apps.quality_safety.services import DeficiencyService

        org, user = org_and_user
        deficiency = self._make_deficiency(org, project, status="resolved")
        with pytest.raises(ValueError):
            DeficiencyService.resolve(deficiency, notes="Again", resolved_by=user)

    def test_verify_transitions_resolved_to_verified(self, db, org_and_user, project):
        from apps.quality_safety.models import Deficiency
        from apps.quality_safety.services import DeficiencyService

        org, user = org_and_user
        deficiency = self._make_deficiency(org, project, status="resolved")
        deficiency = DeficiencyService.verify(deficiency, verifier=user)

        assert deficiency.status == Deficiency.Status.VERIFIED
        assert deficiency.verified_by == user

    def test_reopen_from_resolved(self, db, org_and_user, project):
        from apps.quality_safety.models import Deficiency
        from apps.quality_safety.services import DeficiencyService

        org, user = org_and_user
        deficiency = self._make_deficiency(org, project, status="resolved")
        deficiency = DeficiencyService.reopen(deficiency, user=user, notes="Failed again")

        assert deficiency.status == Deficiency.Status.IN_PROGRESS
        assert deficiency.resolved_date is None

    def test_reopen_from_open_raises(self, db, org_and_user, project):
        from apps.quality_safety.services import DeficiencyService

        org, user = org_and_user
        deficiency = self._make_deficiency(org, project, status="open")
        with pytest.raises(ValueError):
            DeficiencyService.reopen(deficiency, user=user)


# ---------------------------------------------------------------------------
# SafetyService tests
# ---------------------------------------------------------------------------

class TestSafetyService:

    def _make_incident(self, org, project, status="reported"):
        from django.utils import timezone as django_tz

        from apps.quality_safety.models import SafetyIncident
        from apps.tenants.context import tenant_context

        with tenant_context(org):
            return SafetyIncident.objects.create(
                organization=org,
                project=project,
                incident_date=django_tz.now(),
                incident_type=SafetyIncident.IncidentType.NEAR_MISS,
                severity=SafetyIncident.Severity.FIRST_AID,
                description="Test incident",
                status=status,
            )

    def test_advance_status_forward(self, db, org_and_user, project):
        from apps.quality_safety.models import SafetyIncident
        from apps.quality_safety.services import SafetyService

        org, _ = org_and_user
        incident = self._make_incident(org, project, status="reported")
        incident = SafetyService.advance_status(
            incident, SafetyIncident.IncidentStatus.INVESTIGATING
        )
        assert incident.status == SafetyIncident.IncidentStatus.INVESTIGATING

    def test_advance_status_backward_raises(self, db, org_and_user, project):
        from apps.quality_safety.models import SafetyIncident
        from apps.quality_safety.services import SafetyService

        org, _ = org_and_user
        incident = self._make_incident(org, project, status="investigating")
        with pytest.raises(ValueError):
            SafetyService.advance_status(incident, SafetyIncident.IncidentStatus.REPORTED)

    def test_close_incident(self, db, org_and_user, project):
        from apps.quality_safety.models import SafetyIncident
        from apps.quality_safety.services import SafetyService

        org, _ = org_and_user
        incident = self._make_incident(org, project, status="investigating")
        incident = SafetyService.close_incident(incident, corrective_notes="Fixed hazard.")
        assert incident.status == SafetyIncident.IncidentStatus.CLOSED
        assert "Fixed hazard." in incident.corrective_actions

    def test_close_already_closed_raises(self, db, org_and_user, project):
        from apps.quality_safety.services import SafetyService

        org, _ = org_and_user
        incident = self._make_incident(org, project, status="closed")
        with pytest.raises(ValueError):
            SafetyService.close_incident(incident)


# ---------------------------------------------------------------------------
# QualityAnalyticsService tests
# ---------------------------------------------------------------------------

class TestQualityAnalyticsService:

    def test_get_deficiency_stats_empty(self, db, org_and_user):
        from apps.quality_safety.services import QualityAnalyticsService

        org, _ = org_and_user
        stats = QualityAnalyticsService.get_deficiency_stats(org)
        assert stats["total_open"] == 0
        assert stats["total_resolved"] == 0

    def test_get_deficiency_stats_counts(self, db, org_and_user, project):
        from apps.quality_safety.models import Deficiency
        from apps.quality_safety.services import QualityAnalyticsService
        from apps.tenants.context import tenant_context

        org, _ = org_and_user
        with tenant_context(org):
            Deficiency.objects.create(
                organization=org, project=project,
                title="D1", description="desc", severity="minor", status="open",
            )
            Deficiency.objects.create(
                organization=org, project=project,
                title="D2", description="desc", severity="major", status="resolved",
            )

        stats = QualityAnalyticsService.get_deficiency_stats(org)
        assert stats["total_open"] == 1
        assert stats["total_resolved"] == 1

    def test_get_incident_trends_returns_months(self, db, org_and_user):
        from apps.quality_safety.services import QualityAnalyticsService

        org, _ = org_and_user
        trends = QualityAnalyticsService.get_incident_trends(org, months=3)
        assert len(trends) == 3
        for entry in trends:
            assert "month" in entry
            assert "total" in entry
            assert "osha_reportable" in entry

    def test_get_safety_summary(self, db, org_and_user):
        from apps.quality_safety.services import QualityAnalyticsService

        org, _ = org_and_user
        summary = QualityAnalyticsService.get_safety_summary(org)
        assert "incidents_ytd" in summary
        assert "osha_reportable_ytd" in summary
        assert "open_incidents" in summary
        assert "toolbox_talks_ytd" in summary


# ---------------------------------------------------------------------------
# Default checklist seeding test
# ---------------------------------------------------------------------------

class TestChecklistSeeding:

    def test_org_creation_seeds_checklists(self, db):
        """Creating an org seeds default inspection checklist templates."""
        from django.contrib.auth import get_user_model

        from apps.quality_safety.models import InspectionChecklist
        from apps.tenants.models import Organization

        User = get_user_model()
        user = User.objects.create_user(email="seed@test.com", password="test1234!")
        org = Organization.objects.create(
            name="Seed Test Org",
            slug="seed-test-org",
            subscription_status="active",
            owner=user,
        )
        count = InspectionChecklist.objects.filter(organization=org, is_template=True).count()
        assert count >= 5  # at least 5 default checklists seeded
