"""CRM views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import Contact, Deal, PipelineStage
from .serializers import ContactSerializer, DealSerializer, PipelineStageSerializer


class ContactViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["contact_type", "is_active"]
    search_fields = ["first_name", "last_name", "company", "email"]


class PipelineStageViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
    permission_classes = [IsOrganizationMember]


class DealViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["stage", "contact"]
    search_fields = ["title"]
