"""Scheduling signals."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Task

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Task)
def cache_old_task_status(sender, instance, **kwargs):
    """Cache old status before save for comparison in post_save."""
    if instance.pk:
        try:
            old = Task.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Task.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Task)
def on_task_status_changed(sender, instance, created, **kwargs):
    """Log task status changes and trigger critical path recalculation."""
    if created:
        logger.info("Task created: %s (project=%s)", instance.name, instance.project_id)
    elif instance._old_status and instance._old_status != instance.status:
        logger.info(
            "Task status changed: %s → %s (task=%s)",
            instance._old_status,
            instance.status,
            instance.id,
        )
        if instance.status in (Task.Status.COMPLETED, Task.Status.CANCELED):
            from .tasks import recalculate_critical_paths
            recalculate_critical_paths.apply_async(countdown=5)
