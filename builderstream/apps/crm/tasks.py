"""CRM Celery tasks — time-based automations, lead scoring, follow-up reminders."""
import logging
from collections import defaultdict
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="crm.process_time_based_automations")
def process_time_based_automations():
    """Every 15 min — check for time-based automation triggers."""
    from .models import AutomationRule, Lead
    from .services import AutomationEngine

    rules = AutomationRule.objects.filter(is_active=True, trigger_type="time_delay")
    processed = 0

    for rule in rules:
        days_inactive = rule.trigger_config.get("days_inactive", 7)
        cutoff = timezone.now() - timedelta(days=days_inactive)

        leads = Lead.objects.filter(
            organization=rule.organization,
            last_contacted_at__lt=cutoff,
            pipeline_stage__is_won_stage=False,
            pipeline_stage__is_lost_stage=False,
        )

        if leads.exists():
            AutomationEngine.process_automation_rule(rule, leads)
            processed += leads.count()

    logger.info("Processed %d time-based automations", processed)
    return processed


@shared_task(name="crm.calculate_lead_scores")
def calculate_lead_scores():
    """Hourly — recalculate lead scores for all active leads."""
    from .models import Lead
    from .services import LeadScoringService

    leads = Lead.objects.filter(
        pipeline_stage__is_won_stage=False,
        pipeline_stage__is_lost_stage=False,
    ).select_related("contact")

    count = 0
    for lead in leads.iterator():
        try:
            LeadScoringService.calculate_lead_score(lead)
            count += 1
        except Exception:
            logger.exception("Failed to calculate lead score for %s", lead.pk)

    logger.info("Recalculated lead scores for %d leads", count)
    return count


@shared_task(name="crm.send_follow_up_reminders")
def send_follow_up_reminders():
    """Daily — notify assigned users of leads needing follow-up."""
    from .models import Lead

    today = timezone.now().date()
    leads = (
        Lead.objects.filter(
            next_follow_up__date=today,
            pipeline_stage__is_won_stage=False,
            pipeline_stage__is_lost_stage=False,
            assigned_to__isnull=False,
        )
        .select_related("assigned_to", "contact")
    )

    # Group by assigned_to
    by_user = defaultdict(list)
    for lead in leads:
        by_user[lead.assigned_to].append(lead)

    # Send notifications (email or in-app)
    for user, user_leads in by_user.items():
        # TODO: Implement actual email notification
        logger.info(
            "Reminder: %d leads need follow-up for %s (%s)",
            len(user_leads),
            user.get_full_name(),
            user.email,
        )

    total_reminders = sum(len(leads) for leads in by_user.values())
    logger.info("Sent %d follow-up reminders to %d users", total_reminders, len(by_user))
    return total_reminders
