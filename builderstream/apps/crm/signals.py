"""CRM signals — contact creation, lead stage changes, activity logging."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.projects.models import ActivityLog

from .models import Contact, Lead, PipelineStage

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Contact)
def on_contact_created(sender, instance, created, **kwargs):
    """Auto-create Lead when LEAD contact type created, log activity."""
    if created:
        # Log activity
        ActivityLog.objects.create(
            organization=instance.organization,
            action="created",
            entity_type="contact",
            entity_id=instance.pk,
            description=f"Contact '{instance.first_name} {instance.last_name}' created",
        )

        # Auto-create Lead for LEAD contact type
        if instance.contact_type == "lead":
            try:
                first_stage = PipelineStage.objects.filter(
                    organization=instance.organization,
                ).order_by("sort_order").first()

                if first_stage:
                    Lead.objects.get_or_create(
                        organization=instance.organization,
                        contact=instance,
                        defaults={
                            "pipeline_stage": first_stage,
                            "urgency": "warm",
                        },
                    )
                    logger.info("Auto-created lead for contact %s", instance.pk)
            except Exception:
                logger.exception("Failed to auto-create lead for contact %s", instance.pk)


@receiver(pre_save, sender=Lead)
def cache_old_stage(sender, instance, **kwargs):
    """Cache old pipeline stage for change detection."""
    if instance.pk:
        try:
            old = Lead.objects.unscoped().only("pipeline_stage_id").get(pk=instance.pk)
            instance._old_stage_id = old.pipeline_stage_id
        except Lead.DoesNotExist:
            instance._old_stage_id = None
    else:
        instance._old_stage_id = None


@receiver(post_save, sender=Lead)
def on_lead_stage_changed(sender, instance, created, **kwargs):
    """Trigger automations and log activity on stage change."""
    if created:
        # Log lead creation
        ActivityLog.objects.create(
            organization=instance.organization,
            action="created",
            entity_type="lead",
            entity_id=instance.pk,
            description=f"Lead created for '{instance.contact.first_name} {instance.contact.last_name}'",
        )
        return

    # Detect stage change
    old_stage_id = getattr(instance, "_old_stage_id", None)
    if old_stage_id and old_stage_id != instance.pipeline_stage_id:
        # Log activity
        ActivityLog.objects.create(
            organization=instance.organization,
            action="status_changed",
            entity_type="lead",
            entity_id=instance.pk,
            description=f"Lead moved to stage '{instance.pipeline_stage.name}'",
            metadata={
                "old_stage_id": str(old_stage_id),
                "new_stage_id": str(instance.pipeline_stage_id),
            },
        )

        # Trigger automations
        from .models import AutomationRule
        from .services import AutomationEngine

        rules = AutomationRule.objects.filter(
            organization=instance.organization,
            is_active=True,
            trigger_type="stage_change",
        )

        for rule in rules:
            if rule.trigger_config.get("stage_id") == str(instance.pipeline_stage_id):
                try:
                    AutomationEngine.process_automation_rule(rule, [instance])
                except Exception:
                    logger.exception(
                        "Failed to process automation rule %s for lead %s",
                        rule.pk,
                        instance.pk,
                    )
