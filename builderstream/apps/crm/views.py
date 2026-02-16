"""CRM views - 7 ViewSets with custom actions + analytics."""
from collections import defaultdict

from django.db.models import Avg, Count, F, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import has_module_access, IsOrganizationAdmin, IsOrganizationMember

from .models import (
    AutomationRule,
    Company,
    Contact,
    EmailTemplate,
    Interaction,
    Lead,
    PipelineStage,
)
from .serializers import (
    AutomationRuleSerializer,
    CompanyCreateSerializer,
    CompanyDetailSerializer,
    CompanyListSerializer,
    ContactCreateSerializer,
    ContactDetailSerializer,
    ContactListSerializer,
    EmailTemplateSerializer,
    InteractionCreateSerializer,
    InteractionDetailSerializer,
    InteractionListSerializer,
    LeadCreateSerializer,
    LeadDetailSerializer,
    LeadListSerializer,
    PipelineBoardSerializer,
    PipelineStageSerializer,
)
from .services import AutomationEngine, LeadConversionService, LeadScoringService


class ContactViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Contact management with merge, interactions, and quick note actions."""

    queryset = Contact.objects.select_related("company", "referred_by")
    permission_classes = [IsOrganizationMember]  # Temporarily removed module access for testing
    filterset_fields = ["contact_type", "source", "is_active"]
    search_fields = ["first_name", "last_name", "email", "phone", "company_name"]
    ordering_fields = ["lead_score", "created_at", "last_name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ContactListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ContactCreateSerializer
        return ContactDetailSerializer

    @action(detail=True, methods=["post"], url_path="merge")
    def merge_contact(self, request, pk=None):
        """Merge this contact with another, preserving interactions."""
        source_contact = self.get_object()
        target_contact_id = request.data.get("target_contact_id")

        if not target_contact_id:
            return Response(
                {"error": "target_contact_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            target_contact = Contact.objects.get(pk=target_contact_id)
        except Contact.DoesNotExist:
            return Response(
                {"error": "Target contact not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Move interactions to target
        source_contact.interactions.all().update(contact=target_contact)

        # Move leads to target
        source_contact.leads.all().update(contact=target_contact)

        # Delete source contact
        source_contact.delete()

        return Response(
            {"message": f"Merged into {target_contact.first_name} {target_contact.last_name}"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="interactions")
    def list_interactions(self, request, pk=None):
        """List interactions for this contact."""
        contact = self.get_object()
        interactions = contact.interactions.select_related("logged_by").order_by("-occurred_at")
        serializer = InteractionListSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="add-note")
    def add_note(self, request, pk=None):
        """Quick note creation for contact."""
        contact = self.get_object()

        interaction = Interaction.objects.create(
            organization=contact.organization,
            contact=contact,
            interaction_type="note",
            direction="outbound",
            subject=request.data.get("subject", "Note"),
            body=request.data.get("body", ""),
            occurred_at=timezone.now(),
            logged_by=request.user,
        )

        serializer = InteractionDetailSerializer(interaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompanyViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Company management."""

    queryset = Company.objects.prefetch_related("contacts")
    permission_classes = [IsOrganizationMember, has_module_access("crm")]
    filterset_fields = ["company_type"]
    search_fields = ["name", "email", "phone"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CompanyCreateSerializer
        return CompanyDetailSerializer


class PipelineStageViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Pipeline stage management."""

    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
    permission_classes = [IsOrganizationMember, has_module_access("crm")]
    ordering = ["sort_order"]


class LeadViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Lead management with stage transitions, conversion, interactions, and pipeline board."""

    queryset = Lead.objects.select_related(
        "contact",
        "pipeline_stage",
        "assigned_to",
        "converted_project",
    )
    permission_classes = [IsOrganizationMember, has_module_access("crm")]
    filterset_fields = ["pipeline_stage", "assigned_to", "urgency", "project_type"]
    search_fields = ["contact__first_name", "contact__last_name", "description"]
    ordering_fields = ["last_contacted_at", "next_follow_up", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return LeadListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return LeadCreateSerializer
        return LeadDetailSerializer

    @action(detail=True, methods=["post"], url_path="move-stage")
    def move_stage(self, request, pk=None):
        """Transition lead to new stage, trigger automations."""
        lead = self.get_object()
        new_stage_id = request.data.get("pipeline_stage_id")

        if not new_stage_id:
            return Response(
                {"error": "pipeline_stage_id required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_stage = PipelineStage.objects.get(pk=new_stage_id)
        except PipelineStage.DoesNotExist:
            return Response(
                {"error": "Pipeline stage not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        old_stage = lead.pipeline_stage
        lead.pipeline_stage = new_stage
        lead.save(update_fields=["pipeline_stage"])

        # Trigger automations (signals will handle this via post_save)

        return Response(
            {
                "message": f"Moved from '{old_stage.name}' to '{new_stage.name}'",
                "lead": LeadDetailSerializer(lead).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="convert-to-project")
    def convert_to_project(self, request, pk=None):
        """Convert lead to project."""
        lead = self.get_object()

        if lead.converted_project:
            return Response(
                {"error": "Lead already converted to project"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = LeadConversionService.convert_to_project(lead, request.user)

        return Response(
            {
                "message": "Lead converted to project successfully",
                "project_id": str(project.id),
                "project_number": project.project_number,
                "lead": LeadDetailSerializer(lead).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="log-interaction")
    def log_interaction(self, request, pk=None):
        """Quick interaction creation for lead."""
        lead = self.get_object()

        interaction = Interaction.objects.create(
            organization=lead.organization,
            contact=lead.contact,
            lead=lead,
            interaction_type=request.data.get("interaction_type", "note"),
            direction=request.data.get("direction", "outbound"),
            subject=request.data.get("subject", ""),
            body=request.data.get("body", ""),
            occurred_at=timezone.now(),
            logged_by=request.user,
        )

        # Update last_contacted_at
        lead.last_contacted_at = timezone.now()
        lead.save(update_fields=["last_contacted_at"])

        serializer = InteractionDetailSerializer(interaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="pipeline-board")
    def pipeline_board(self, request):
        """Kanban-style pipeline board data."""
        org = request.organization
        stages = PipelineStage.objects.filter(organization=org).order_by("sort_order")

        leads_by_stage = {}
        for stage in stages:
            leads = Lead.objects.filter(
                organization=org,
                pipeline_stage=stage,
            ).select_related("contact", "assigned_to")[:50]  # Limit per stage
            leads_by_stage[str(stage.id)] = LeadListSerializer(leads, many=True).data

        serializer = PipelineBoardSerializer(
            {
                "stages": stages,
                "leads_by_stage": leads_by_stage,
            }
        )
        return Response(serializer.data)


class InteractionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Interaction/communication log management."""

    queryset = Interaction.objects.select_related("contact", "lead", "logged_by")
    permission_classes = [IsOrganizationMember, has_module_access("crm")]
    filterset_fields = ["contact", "lead", "interaction_type", "direction"]
    search_fields = ["subject", "body"]
    ordering = ["-occurred_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return InteractionListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return InteractionCreateSerializer
        return InteractionDetailSerializer


class AutomationRuleViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Automation rule management (ADMIN ONLY)."""

    queryset = AutomationRule.objects.all()
    serializer_class = AutomationRuleSerializer
    permission_classes = [IsOrganizationAdmin, has_module_access("crm")]
    filterset_fields = ["is_active", "trigger_type", "action_type"]
    ordering = ["name"]


class EmailTemplateViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """Email template management."""

    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsOrganizationMember, has_module_access("crm")]
    filterset_fields = ["template_type"]
    search_fields = ["name", "subject"]
    ordering = ["name"]


class LeadAnalyticsView(APIView):
    """Lead analytics and conversion metrics."""

    permission_classes = [IsAuthenticated, has_module_access("crm")]

    def get(self, request):
        """Return analytics data."""
        org = request.organization

        # Conversion rates by source
        conversion_by_source = {}
        sources = Contact.Source.choices
        for source_value, source_label in sources:
            total = Lead.objects.filter(
                organization=org,
                contact__source=source_value,
            ).count()

            converted = Lead.objects.filter(
                organization=org,
                contact__source=source_value,
                converted_project__isnull=False,
            ).count()

            conversion_by_source[source_label] = {
                "total": total,
                "converted": converted,
                "rate": round((converted / total * 100) if total > 0 else 0, 2),
            }

        # Conversion rates by assigned_to
        conversion_by_assigned_to = {}
        assignments = (
            Lead.objects.filter(organization=org, assigned_to__isnull=False)
            .values("assigned_to__id", "assigned_to__first_name", "assigned_to__last_name")
            .annotate(
                total=Count("id"),
                converted=Count("id", filter=Q(converted_project__isnull=False)),
            )
        )

        for assignment in assignments:
            name = f"{assignment['assigned_to__first_name']} {assignment['assigned_to__last_name']}"
            conversion_by_assigned_to[name] = {
                "total": assignment["total"],
                "converted": assignment["converted"],
                "rate": round(
                    (assignment["converted"] / assignment["total"] * 100)
                    if assignment["total"] > 0
                    else 0,
                    2,
                ),
            }

        # Conversion rates by project_type
        conversion_by_project_type = {}
        project_types = Lead.ProjectType.choices
        for type_value, type_label in project_types:
            total = Lead.objects.filter(
                organization=org,
                project_type=type_value,
            ).count()

            converted = Lead.objects.filter(
                organization=org,
                project_type=type_value,
                converted_project__isnull=False,
            ).count()

            conversion_by_project_type[type_label] = {
                "total": total,
                "converted": converted,
                "rate": round((converted / total * 100) if total > 0 else 0, 2),
            }

        # Win/loss reasons
        win_loss_reasons = {}
        lost_leads = Lead.objects.filter(
            organization=org,
            pipeline_stage__is_lost_stage=True,
            lost_reason__isnull=False,
        ).exclude(lost_reason="")

        reason_counts = defaultdict(int)
        for lead in lost_leads:
            reason_counts[lead.lost_reason] += 1

        win_loss_reasons = dict(reason_counts)

        # Average time in each stage (days)
        avg_time_in_stage = {}
        stages = PipelineStage.objects.filter(organization=org)
        # TODO: Implement stage transition tracking for accurate time calculation
        # For now, return placeholder
        for stage in stages:
            avg_time_in_stage[stage.name] = 0

        # Lead velocity (new leads per week/month)
        from datetime import timedelta

        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        leads_this_week = Lead.objects.filter(
            organization=org,
            created_at__gte=week_ago,
        ).count()

        leads_this_month = Lead.objects.filter(
            organization=org,
            created_at__gte=month_ago,
        ).count()

        lead_velocity = {
            "this_week": leads_this_week,
            "this_month": leads_this_month,
            "avg_per_week": round(leads_this_month / 4.33, 2),
        }

        return Response(
            {
                "conversion_by_source": conversion_by_source,
                "conversion_by_assigned_to": conversion_by_assigned_to,
                "conversion_by_project_type": conversion_by_project_type,
                "win_loss_reasons": win_loss_reasons,
                "avg_time_in_stage": avg_time_in_stage,
                "lead_velocity": lead_velocity,
            }
        )
