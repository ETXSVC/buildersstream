"""Quality & Safety signals."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="quality_safety.Inspection")
def on_inspection_saved(sender, instance, created, **kwargs):
    """Log when an inspection status changes to a final state."""
    if created:
        logger.info(
            "Inspection created: %s for project %s", instance.pk, instance.project_id
        )
        return

    final_statuses = {"passed", "failed", "conditional"}
    if instance.status in final_statuses:
        logger.info(
            "Inspection %s finalized with status '%s', score=%s",
            instance.pk, instance.status, instance.overall_score,
        )


@receiver(post_save, sender="quality_safety.SafetyIncident")
def on_safety_incident_saved(sender, instance, created, **kwargs):
    """Log OSHA-reportable incidents."""
    if created and instance.osha_reportable:
        logger.warning(
            "OSHA-reportable incident created: %s in project %s (severity: %s)",
            instance.pk, instance.project_id, instance.severity,
        )


@receiver(post_save, sender="quality_safety.Deficiency")
def on_deficiency_saved(sender, instance, created, **kwargs):
    """Log critical deficiencies when created."""
    if created and instance.severity == "critical":
        logger.warning(
            "Critical deficiency created: '%s' in project %s",
            instance.title, instance.project_id,
        )
