"""Scheduling Celery tasks."""
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="scheduling.recalculate_critical_paths")
def recalculate_critical_paths():
    """Recalculate critical path flags for all active projects (hourly)."""
    from apps.projects.models import Project
    from .services import CriticalPathService

    active_statuses = [
        "prospect", "estimate", "proposal", "contract",
        "production", "punch_list", "closeout",
    ]

    projects = Project.objects.unscoped().filter(
        is_active=True, is_archived=False, status__in=active_statuses
    )

    count = 0
    for project in projects.iterator():
        try:
            service = CriticalPathService(project)
            service.calculate()
            count += 1
        except Exception:
            logger.exception("Error recalculating critical path for project %s", project.id)

    logger.info("Recalculated critical paths for %d projects", count)
    return count


@shared_task(name="scheduling.check_schedule_conflicts")
def check_schedule_conflicts():
    """Scan for resource conflicts and create action items (daily)."""
    from apps.tenants.models import Organization
    from .services import ScheduleConflictService

    orgs = Organization.objects.filter(is_active=True)
    total_conflicts = 0

    for org in orgs.iterator():
        try:
            service = ScheduleConflictService(org)
            conflicts = service.detect_all_conflicts()
            crew_conflicts = conflicts.get("crew_conflicts", [])
            equip_conflicts = conflicts.get("equipment_conflicts", [])
            conflict_count = len(crew_conflicts) + len(equip_conflicts)
            if conflict_count:
                logger.warning(
                    "Org %s has %d crew conflicts and %d equipment conflicts",
                    org.slug, len(crew_conflicts), len(equip_conflicts),
                )
            total_conflicts += conflict_count
        except Exception:
            logger.exception("Error checking conflicts for org %s", org.id)

    logger.info("Schedule conflict check complete. Total conflicts: %d", total_conflicts)
    return total_conflicts


@shared_task(name="scheduling.calculate_equipment_depreciation")
def calculate_equipment_depreciation():
    """Update equipment book values based on depreciation (monthly)."""
    from .models import Equipment

    equipment_list = Equipment.objects.unscoped().exclude(
        status=Equipment.Status.RETIRED
    )

    updated = 0
    for equip in equipment_list.iterator():
        try:
            new_value = equip.calculate_book_value()
            if round(float(equip.current_book_value), 2) != round(new_value, 2):
                equip.current_book_value = new_value
                equip.save(update_fields=["current_book_value"])
                updated += 1
        except Exception:
            logger.exception("Error calculating depreciation for equipment %s", equip.id)

    logger.info("Equipment depreciation: updated %d records", updated)
    return updated
