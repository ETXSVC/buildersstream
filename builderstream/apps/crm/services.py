"""CRM service layer — lead scoring, conversion, automation."""
import logging
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


class LeadScoringService:
    """Calculate lead scores based on multiple factors (0-100)."""

    @staticmethod
    def calculate_lead_score(lead):
        """
        Calculate lead score based on:
        - Estimated value (30 points)
        - Urgency (20 points)
        - Source quality (20 points)
        - Engagement/interactions (20 points)
        - Response time (10 points)

        Returns score (0-100) and updates contact.lead_score.
        """
        score = 0

        # Estimated value (30 points)
        if lead.estimated_value:
            if lead.estimated_value >= 500000:
                score += 30
            elif lead.estimated_value >= 100000:
                score += 20
            elif lead.estimated_value >= 50000:
                score += 10
            elif lead.estimated_value >= 25000:
                score += 5

        # Urgency (20 points)
        if lead.urgency == "hot":
            score += 20
        elif lead.urgency == "warm":
            score += 10
        elif lead.urgency == "cold":
            score += 5

        # Source quality (20 points)
        source_scores = {
            "referral": 20,
            "home_advisor": 15,
            "angi": 15,
            "website_form": 12,
            "houzz": 12,
            "home_show": 10,
            "phone": 8,
            "email": 8,
            "social_media": 6,
            "walk_in": 5,
            "other": 3,
        }
        score += source_scores.get(lead.contact.source, 0)

        # Engagement (20 points) - interaction count
        interaction_count = lead.interactions.count()
        if interaction_count >= 5:
            score += 20
        elif interaction_count >= 3:
            score += 15
        elif interaction_count >= 2:
            score += 10
        elif interaction_count >= 1:
            score += 5

        # Response time (10 points) - days since last contact
        if lead.last_contacted_at:
            days_since = (timezone.now() - lead.last_contacted_at).days
            if days_since <= 1:
                score += 10
            elif days_since <= 3:
                score += 7
            elif days_since <= 7:
                score += 5
            elif days_since <= 14:
                score += 2

        # Cap at 100
        final_score = min(100, score)

        # Update contact lead_score
        lead.contact.lead_score = final_score
        lead.contact.save(update_fields=["lead_score"])

        logger.debug("Calculated lead score %d for lead %s", final_score, lead.pk)
        return final_score


class LeadConversionService:
    """Convert leads to projects."""

    @staticmethod
    def convert_to_project(lead, user):
        """
        Convert lead to project, link contact as client.

        Creates a new Project from the Lead and:
        - Links contact as Project.client
        - Moves lead to Won stage
        - Links back to lead via converted_project
        - Logs activity

        Returns created Project instance.
        """
        from apps.projects.models import ActivityLog, Project
        from apps.projects.services import ProjectNumberService

        from .models import PipelineStage

        # Generate project name
        contact = lead.contact
        project_name = (
            f"{contact.first_name} {contact.last_name} - "
            f"{lead.get_project_type_display() if lead.project_type else 'Project'}"
        )

        # Create Project
        project = Project.objects.create(
            organization=lead.organization,
            name=project_name,
            project_number=ProjectNumberService.generate_project_number(lead.organization),
            client=contact,
            project_type=lead.project_type if lead.project_type else "other",
            status="lead",
            estimated_value=lead.estimated_value,
            start_date=lead.estimated_start,
            description=lead.description,
            project_manager=lead.assigned_to,
            created_by=user,
        )

        logger.info("Created project %s from lead %s", project.pk, lead.pk)

        # Update lead - move to Won stage and link project
        try:
            won_stage = PipelineStage.objects.get(
                organization=lead.organization,
                is_won_stage=True,
            )
            lead.pipeline_stage = won_stage
        except PipelineStage.DoesNotExist:
            logger.warning(
                "No Won stage found for org %s, keeping current stage",
                lead.organization.pk,
            )

        lead.converted_project = project
        lead.save(update_fields=["converted_project", "pipeline_stage"])

        # Log activity
        ActivityLog.objects.create(
            organization=lead.organization,
            user=user,
            action="created",
            entity_type="project_from_lead",
            entity_id=project.pk,
            description=f"Converted lead '{lead.id}' to project '{project.name}'",
            metadata={
                "lead_id": str(lead.id),
                "lead_contact": f"{contact.first_name} {contact.last_name}",
                "project_id": str(project.id),
                "project_number": project.project_number,
            },
        )

        logger.info("Converted lead %s to project %s", lead.pk, project.pk)
        return project


class AutomationEngine:
    """Process automation rules and execute actions."""

    @staticmethod
    def process_automation_rule(rule, leads_or_contacts):
        """
        Execute automation rule for matching leads/contacts.

        Supports actions:
        - SEND_EMAIL
        - SEND_SMS
        - CREATE_TASK (ActionItem)
        - ASSIGN_LEAD
        - CHANGE_STAGE
        - NOTIFY_USER

        Args:
            rule: AutomationRule instance
            leads_or_contacts: Queryset of Lead or Contact instances
        """
        from apps.projects.models import ActionItem

        from .models import EmailTemplate

        action_type = rule.action_type
        action_config = rule.action_config

        logger.info(
            "Processing automation rule '%s' (%s) for %d entities",
            rule.name,
            action_type,
            leads_or_contacts.count(),
        )

        # SEND_EMAIL action
        if action_type == "send_email":
            template_id = action_config.get("template_id")
            if not template_id:
                logger.warning("No template_id in action_config for rule %s", rule.pk)
                return

            try:
                template = EmailTemplate.objects.get(pk=template_id)
            except EmailTemplate.DoesNotExist:
                logger.error("Email template %s not found", template_id)
                return

            for entity in leads_or_contacts:
                contact = entity.contact if hasattr(entity, "contact") else entity
                if not contact.email:
                    continue

                # TODO: Implement actual email sending via Celery task
                # send_email_task.delay(contact.email, template.id, entity.id)
                logger.info(
                    "Would send email '%s' to %s (template: %s)",
                    template.subject,
                    contact.email,
                    template.name,
                )

        # SEND_SMS action
        elif action_type == "send_sms":
            # TODO: Implement SMS sending
            for entity in leads_or_contacts:
                contact = entity.contact if hasattr(entity, "contact") else entity
                phone = contact.mobile_phone or contact.phone
                if phone:
                    logger.info("Would send SMS to %s", phone)

        # CREATE_TASK action
        elif action_type == "create_task":
            task_title = action_config.get("task_title", "Follow up needed")
            task_description = action_config.get("task_description", "")
            assign_to_id = action_config.get("assign_to_id")
            due_in_days = action_config.get("due_in_days", 1)

            for entity in leads_or_contacts:
                # Determine assigned_to
                if assign_to_id:
                    assigned_to_id = assign_to_id
                elif hasattr(entity, "assigned_to") and entity.assigned_to:
                    assigned_to_id = entity.assigned_to.pk
                else:
                    assigned_to_id = None

                ActionItem.objects.create(
                    organization=entity.organization,
                    title=task_title,
                    description=task_description,
                    assigned_to_id=assigned_to_id,
                    due_date=timezone.now() + timedelta(days=due_in_days),
                    item_type="task",
                    priority="medium",
                )

                logger.info("Created task '%s' for entity %s", task_title, entity.pk)

        # ASSIGN_LEAD action
        elif action_type == "assign_lead":
            assign_to_id = action_config.get("assign_to_id")
            if not assign_to_id:
                logger.warning("No assign_to_id in action_config for rule %s", rule.pk)
                return

            for entity in leads_or_contacts:
                if hasattr(entity, "assigned_to"):
                    entity.assigned_to_id = assign_to_id
                    entity.save(update_fields=["assigned_to"])
                    logger.info("Assigned lead %s to user %s", entity.pk, assign_to_id)

        # CHANGE_STAGE action
        elif action_type == "change_stage":
            from .models import PipelineStage

            stage_id = action_config.get("stage_id")
            if not stage_id:
                logger.warning("No stage_id in action_config for rule %s", rule.pk)
                return

            try:
                new_stage = PipelineStage.objects.get(pk=stage_id)
            except PipelineStage.DoesNotExist:
                logger.error("Pipeline stage %s not found", stage_id)
                return

            for entity in leads_or_contacts:
                if hasattr(entity, "pipeline_stage"):
                    entity.pipeline_stage = new_stage
                    entity.save(update_fields=["pipeline_stage"])
                    logger.info(
                        "Moved lead %s to stage '%s'",
                        entity.pk,
                        new_stage.name,
                    )

        # NOTIFY_USER action
        elif action_type == "notify_user":
            user_id = action_config.get("user_id")
            message = action_config.get("message", "Automation notification")

            # TODO: Implement user notification system
            logger.info("Would notify user %s: %s", user_id, message)

        else:
            logger.warning("Unknown action_type '%s' for rule %s", action_type, rule.pk)
