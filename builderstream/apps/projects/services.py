"""Project services — lifecycle management, dashboard aggregation, project numbering."""
import logging
from datetime import date, timedelta

from django.core.cache import cache
from django.db.models import Count, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProjectNumberService:
    """Generates auto-incrementing project numbers per organization per year."""

    @staticmethod
    def generate_project_number(organization):
        """Generate next project number: BSP-{YEAR}-{SEQ:03d}."""
        from .models import Project

        current_year = timezone.now().year
        prefix = f"BSP-{current_year}-"

        last_project = (
            Project.objects.unscoped()
            .filter(
                organization=organization,
                project_number__startswith=prefix,
            )
            .order_by("-project_number")
            .first()
        )

        if last_project:
            try:
                last_seq = int(last_project.project_number.split("-")[-1])
                next_seq = last_seq + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:03d}"


class ProjectLifecycleService:
    """Manages project status transitions and health scoring."""

    VALID_TRANSITIONS = {
        "lead": ["prospect", "canceled"],
        "prospect": ["estimate", "lead", "canceled"],
        "estimate": ["proposal", "prospect", "canceled"],
        "proposal": ["contract", "estimate", "canceled"],
        "contract": ["production", "proposal", "canceled"],
        "production": ["punch_list", "canceled"],
        "punch_list": ["closeout", "production", "canceled"],
        "closeout": ["completed", "punch_list"],
        "completed": [],
        "canceled": ["lead"],
    }

    STAGE_REQUIREMENTS = {
        "contract": ["client_assigned", "estimated_value_set"],
        "production": ["start_date_set", "team_assigned"],
        "completed": ["actual_completion_set"],
    }

    @staticmethod
    def transition_status(project, new_status, user, notes=""):
        """Transition a project to a new status with validation."""
        from .models import ProjectStageTransition

        old_status = project.status

        allowed = ProjectLifecycleService.VALID_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition from '{old_status}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )

        requirements = ProjectLifecycleService.STAGE_REQUIREMENTS.get(new_status, [])
        requirements_met = {}
        for req in requirements:
            met = ProjectLifecycleService._check_requirement(project, req)
            requirements_met[req] = met
            if not met:
                raise ValueError(f"Stage-gate requirement not met: {req}")

        project.status = new_status
        project.save(update_fields=["status", "updated_at"])

        ProjectStageTransition.objects.create(
            project=project,
            from_status=old_status,
            to_status=new_status,
            transitioned_by=user,
            notes=notes,
            requirements_met=requirements_met,
        )

        logger.info("Project %s transitioned %s -> %s by %s", project, old_status, new_status, user)
        return project

    @staticmethod
    def _check_requirement(project, requirement):
        """Check if a specific stage-gate requirement is met."""
        checks = {
            "client_assigned": lambda p: p.client_id is not None,
            "estimated_value_set": lambda p: (
                p.estimated_value is not None and p.estimated_value > 0
            ),
            "start_date_set": lambda p: p.start_date is not None,
            "team_assigned": lambda p: p.team_members.exists(),
            "actual_completion_set": lambda p: p.actual_completion is not None,
        }
        check_fn = checks.get(requirement)
        if check_fn is None:
            return True
        return check_fn(project)

    @staticmethod
    def calculate_health_score(project):
        """Calculate project health score (0-100) and status (GREEN/YELLOW/RED)."""
        from .models import ActionItem

        score = 100

        # Budget variance (40 points max deduction)
        if project.estimated_value and project.actual_cost:
            budget_ratio = float(project.actual_cost / project.estimated_value)
            if budget_ratio > 1.15:
                score -= 40
            elif budget_ratio > 1.05:
                score -= 20
            elif budget_ratio > 1.0:
                score -= 10

        # Schedule variance (30 points max deduction)
        if project.estimated_completion and not project.actual_completion:
            today = date.today()
            if today > project.estimated_completion:
                days_overdue = (today - project.estimated_completion).days
                if days_overdue > 30:
                    score -= 30
                elif days_overdue > 14:
                    score -= 20
                elif days_overdue > 0:
                    score -= 10

        # Overdue action items (30 points max deduction)
        overdue_count = ActionItem.objects.filter(
            project=project,
            is_resolved=False,
            due_date__lt=date.today(),
        ).count()
        if overdue_count > 5:
            score -= 30
        elif overdue_count > 2:
            score -= 15
        elif overdue_count > 0:
            score -= 10

        score = max(0, min(100, score))

        if score >= 70:
            health_status = "green"
        elif score >= 40:
            health_status = "yellow"
        else:
            health_status = "red"

        project.health_score = score
        project.health_status = health_status
        project.save(update_fields=["health_score", "health_status", "updated_at"])

        return score, health_status


class DashboardService:
    """Aggregates dashboard data for the organization."""

    CACHE_TTL = 60  # seconds

    @staticmethod
    def get_dashboard_data(organization, user):
        """Return aggregated dashboard data, with Redis caching."""
        cache_key = f"dashboard:{organization.pk}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        data = DashboardService._build_dashboard_data(organization, user)
        cache.set(cache_key, data, DashboardService.CACHE_TTL)
        return data

    @staticmethod
    def _build_dashboard_data(organization, user):
        from .models import ActionItem, ActivityLog, Project

        active_projects = (
            Project.objects.unscoped()
            .filter(
                organization=organization,
                is_active=True,
                is_archived=False,
            )
            .exclude(status__in=["completed", "canceled"])
        )

        # Financial snapshot
        financial = active_projects.aggregate(
            total_estimated_value=Sum("estimated_value"),
            total_actual_revenue=Sum("actual_revenue"),
            total_estimated_cost=Sum("estimated_cost"),
            total_actual_cost=Sum("actual_cost"),
            project_count=Count("id"),
        )

        # Schedule overview
        today = date.today()
        schedule = {
            "projects_on_track": active_projects.filter(health_status="green").count(),
            "projects_at_risk": active_projects.filter(health_status="yellow").count(),
            "projects_behind": active_projects.filter(health_status="red").count(),
            "overdue_projects": active_projects.filter(
                estimated_completion__lt=today,
                actual_completion__isnull=True,
            ).count(),
        }

        # Status distribution
        status_distribution = dict(
            active_projects.values_list("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )

        # Action items (top 20, unresolved)
        action_items = list(
            ActionItem.objects.filter(
                organization=organization,
                is_resolved=False,
            )
            .select_related("project", "assigned_to")
            .order_by("due_date", "-created_at")[:20]
            .values(
                "id", "title", "item_type", "priority",
                "due_date", "project__name", "project__project_number",
                "assigned_to__first_name", "assigned_to__last_name",
            )
        )

        # Activity stream (last 50)
        activity = list(
            ActivityLog.objects.filter(organization=organization)
            .select_related("user", "project")
            .order_by("-created_at")[:50]
            .values(
                "id", "action", "entity_type", "description",
                "created_at", "user__first_name", "user__last_name",
                "project__name", "project__project_number",
            )
        )

        # Weather stub
        weather = {
            "available": False,
            "message": "Weather integration coming soon",
        }

        return {
            "active_projects": {
                "count": financial["project_count"] or 0,
                "status_distribution": status_distribution,
            },
            "financial_snapshot": {
                "total_estimated_value": str(financial["total_estimated_value"] or 0),
                "total_actual_revenue": str(financial["total_actual_revenue"] or 0),
                "total_estimated_cost": str(financial["total_estimated_cost"] or 0),
                "total_actual_cost": str(financial["total_actual_cost"] or 0),
            },
            "schedule_overview": schedule,
            "action_items": action_items,
            "activity_stream": activity,
            "weather": weather,
        }
