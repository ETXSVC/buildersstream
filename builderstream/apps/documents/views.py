"""Document views."""
from rest_framework import viewsets

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember

from .models import Document, Folder, RFI, Submittal
from .serializers import DocumentSerializer, FolderSerializer, RFISerializer, SubmittalSerializer


class FolderViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "parent"]


class DocumentViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "folder"]
    search_fields = ["title", "description"]


class RFIViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = RFI.objects.all()
    serializer_class = RFISerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "assigned_to"]
    search_fields = ["number", "subject"]


class SubmittalViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Submittal.objects.all()
    serializer_class = SubmittalSerializer
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status"]
    search_fields = ["number", "title"]
