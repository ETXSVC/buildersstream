"""Project signals — status tracking, activity logging, default milestones."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import ActivityLog, Project, ProjectMilestone

logger = logging.getLogger(__name__)

DEFAULT_MILESTONES = [
    {"name": "Pre-Construction Meeting", "sort_order": 1},
    {"name": "Permits & Approvals", "sort_order": 2},
    {"name": "Rough-In Inspection", "sort_order": 3},
    {"name": "Mid-Project Review", "sort_order": 4},
    {"name": "Final Walkthrough", "sort_order": 5},
    {"name": "Punch List Complete", "sort_order": 6},
    {"name": "Final Payment Collected", "sort_order": 7},
]


@receiver(pre_save, sender=Project)
def cache_old_status(sender, instance, **kwargs):
    """Cache the previous status so post_save can detect transitions."""
    if instance.pk:
        try:
            old = Project.objects.unscoped().only("status").get(pk=instance.pk)
            instance._old_status = old.status
        except Project.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Project)
def on_project_save(sender, instance, created, **kwargs):
    """Log activity and seed default milestones on create."""
    if created:
        # Log creation activity
        ActivityLog.objects.create(
            organization=instance.organization,
            project=instance,
            user=instance.created_by if hasattr(instance, "created_by") and instance.created_by else None,
            action="created",
            entity_type="project",
            entity_id=instance.pk,
            description=f"Project '{instance.name}' created.",
        )

        # Seed default milestones
        milestones = [
            ProjectMilestone(
                project=instance,
                organization=instance.organization,
                name=m["name"],
                sort_order=m["sort_order"],
            )
            for m in DEFAULT_MILESTONES
        ]
        ProjectMilestone.objects.bulk_create(milestones)
        logger.info("Created %d default milestones for %s", len(milestones), instance)
        return

    # Detect status change on update
    old_status = getattr(instance, "_old_status", None)
    if old_status and old_status != instance.status:
        ActivityLog.objects.create(
            organization=instance.organization,
            project=instance,
            action="status_changed",
            entity_type="project",
            entity_id=instance.pk,
            description=f"Status changed from '{old_status}' to '{instance.status}'.",
            metadata={"from_status": old_status, "to_status": instance.status},
        )
