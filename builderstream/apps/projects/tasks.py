"""Project Celery tasks — health scoring, action-item generation, cache warming."""
import logging
from datetime import date, timedelta

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="projects.calculate_all_health_scores")
def calculate_all_health_scores():
    """Recalculate health scores for all active projects (hourly)."""
    from .models import Project
    from .services import ProjectLifecycleService

    active_statuses = [
        "prospect", "estimate", "proposal", "contract",
        "production", "punch_list", "closeout",
    ]

    projects = (
        Project.objects.unscoped()
        .filter(is_active=True, is_archived=False, status__in=active_statuses)
    )

    count = 0
    for project in projects.iterator():
        try:
            ProjectLifecycleService.calculate_health_score(project)
            count += 1
        except Exception:
            logger.exception("Health score failed for project %s", project.pk)

    logger.info("Recalculated health scores for %d projects.", count)
    return count


@shared_task(name="projects.generate_action_items")
def generate_action_items():
    """Auto-generate action items for overdue projects and upcoming milestones (every 30 min)."""
    from .models import ActionItem, Project, ProjectMilestone

    today = date.today()
    created = 0

    # 1. Overdue projects → action item
    overdue_projects = (
        Project.objects.unscoped()
        .filter(
            is_active=True,
            is_archived=False,
            estimated_completion__lt=today,
            actual_completion__isnull=True,
        )
        .exclude(status__in=["completed", "canceled"])
    )

    for project in overdue_projects.iterator():
        _, was_created = ActionItem.objects.get_or_create(
            organization=project.organization,
            project=project,
            source_type="auto_overdue",
            source_id=project.pk,
            is_resolved=False,
            defaults={
                "title": f"Project '{project.name}' is overdue",
                "description": (
                    f"Estimated completion was {project.estimated_completion}. "
                    "Please update the schedule or mark complete."
                ),
                "item_type": "deadline",
                "priority": "high",
                "assigned_to": project.project_manager,
                "due_date": today,
            },
        )
        if was_created:
            created += 1

    # 2. Milestones due in 7 days → action item
    upcoming = today + timedelta(days=7)
    milestones = (
        ProjectMilestone.objects.filter(
            is_completed=False,
            due_date__isnull=False,
            due_date__lte=upcoming,
            due_date__gte=today,
        )
        .select_related("project", "organization")
    )

    for ms in milestones.iterator():
        _, was_created = ActionItem.objects.get_or_create(
            organization=ms.organization,
            project=ms.project,
            source_type="auto_milestone",
            source_id=ms.pk,
            is_resolved=False,
            defaults={
                "title": f"Milestone '{ms.name}' due {ms.due_date}",
                "description": f"Milestone for project '{ms.project.name}' is approaching.",
                "item_type": "deadline",
                "priority": "medium",
                "assigned_to": ms.project.project_manager if ms.project else None,
                "due_date": ms.due_date,
            },
        )
        if was_created:
            created += 1

    logger.info("Generated %d new action items.", created)
    return created


@shared_task(name="projects.cache_dashboard_data")
def cache_dashboard_data(organization_id):
    """Pre-warm dashboard cache for a specific organization."""
    from apps.tenants.models import Organization

    from .services import DashboardService

    try:
        org = Organization.objects.get(pk=organization_id)
    except Organization.DoesNotExist:
        logger.warning("Organization %s not found for cache warming.", organization_id)
        return

    DashboardService.get_dashboard_data(org, user=None)
    logger.info("Dashboard cache warmed for org %s.", org.pk)
