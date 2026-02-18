"""
Document & Photo Control views.

6 ViewSets:
  DocumentFolderViewSet  - CRUD for folder hierarchy
  DocumentViewSet        - CRUD + upload_url, upload_complete, new_version, download, acknowledge, versions
  RFIViewSet             - CRUD + answer, close, distribute
  SubmittalViewSet       - CRUD + review, submit
  PhotoViewSet           - CRUD + bulk_upload_urls, bulk_create, annotate, download
  PhotoAlbumViewSet      - CRUD + add_photos, remove_photos, set_cover
"""

import logging

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationMember
from apps.documents.models import (
    Document,
    DocumentAcknowledgment,
    DocumentFolder,
    Photo,
    PhotoAlbum,
    RFI,
    Submittal,
)
from apps.documents.serializers import (
    BulkPhotoUploadRequestSerializer,
    DocumentAcknowledgmentSerializer,
    DocumentCreateSerializer,
    DocumentDetailSerializer,
    DocumentFolderCreateSerializer,
    DocumentFolderDetailSerializer,
    DocumentFolderListSerializer,
    DocumentListSerializer,
    PhotoAlbumCreateSerializer,
    PhotoAlbumDetailSerializer,
    PhotoAlbumListSerializer,
    PhotoAnnotateSerializer,
    PhotoCreateSerializer,
    PhotoDetailSerializer,
    PhotoListSerializer,
    PresignedUploadRequestSerializer,
    RFIAnswerSerializer,
    RFICreateSerializer,
    RFIDetailSerializer,
    RFIListSerializer,
    SubmittalCreateSerializer,
    SubmittalDetailSerializer,
    SubmittalListSerializer,
    SubmittalReviewSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DocumentFolder
# ---------------------------------------------------------------------------

class DocumentFolderViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for hierarchical document folders (project-specific or org-level)."""
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "folder_type", "access_level", "parent"]
    search_fields = ["name"]
    ordering_fields = ["sort_order", "name", "created_at"]
    ordering = ["sort_order", "name"]

    def get_queryset(self):
        return DocumentFolder.objects.select_related("project", "parent")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return DocumentFolderCreateSerializer
        if self.action == "retrieve":
            return DocumentFolderDetailSerializer
        return DocumentFolderListSerializer

    def perform_create(self, serializer):
        serializer.save(organization=self.request.current_organization)


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class DocumentViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """
    CRUD for versioned documents stored in S3.

    Upload flow:
      1. POST /upload-url/       - get presigned PUT URL
      2. Client PUTs file to S3
      3. POST /upload-complete/  - create Document record
    """
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["folder", "project", "status", "is_current_version", "requires_acknowledgment"]
    search_fields = ["title", "file_name"]
    ordering_fields = ["created_at", "title", "version"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Document.objects.select_related(
            "folder", "project", "uploaded_by", "previous_version"
        ).filter(is_current_version=True)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentListSerializer

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use POST /upload-url/ then POST /upload-complete/."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["post"], url_path="upload-url")
    def upload_url(self, request):
        """Generate a presigned S3 PUT URL for direct file upload."""
        serializer = PresignedUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.documents.services import FileUploadService
        org = request.current_organization
        project_id = serializer.validated_data.get("project")
        try:
            result = FileUploadService.generate_upload_url(
                organization_id=str(org.id),
                project_id=str(project_id) if project_id else None,
                file_name=serializer.validated_data["file_name"],
                content_type=serializer.validated_data["content_type"],
                file_type="document",
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.error("upload_url error: %s", exc)
            return Response({"detail": "Failed to generate upload URL."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=["post"], url_path="upload-complete")
    def upload_complete(self, request):
        """Create a Document record after the file has been uploaded to S3."""
        serializer = DocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        org = request.current_organization

        folder = None
        if data.get("folder"):
            try:
                folder = DocumentFolder.objects.get(pk=data["folder"], organization=org)
            except DocumentFolder.DoesNotExist:
                return Response({"folder": "Folder not found."}, status=status.HTTP_400_BAD_REQUEST)

        project = None
        if data.get("project"):
            from apps.projects.models import Project
            try:
                project = Project.objects.get(pk=data["project"], organization=org)
            except Project.DoesNotExist:
                return Response({"project": "Project not found."}, status=status.HTTP_400_BAD_REQUEST)

        doc = Document.objects.create(
            organization=org,
            folder=folder,
            project=project,
            title=data["title"],
            description=data.get("description", ""),
            file_key=data["file_key"],
            file_name=data["file_name"],
            file_size=data["file_size"],
            content_type=data["content_type"],
            tags=data.get("tags", []),
            requires_acknowledgment=data.get("requires_acknowledgment", False),
            uploaded_by=request.user,
            version=1,
            is_current_version=True,
        )
        return Response(DocumentDetailSerializer(doc).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="new-version")
    def new_version(self, request, pk=None):
        """Upload a new version of an existing document."""
        old_doc = self.get_object()
        serializer = PresignedUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.documents.services import FileUploadService
        org = request.current_organization
        if "file_key" not in request.data:
            result = FileUploadService.generate_upload_url(
                organization_id=str(org.id),
                project_id=str(old_doc.project_id) if old_doc.project_id else None,
                file_name=serializer.validated_data["file_name"],
                content_type=serializer.validated_data["content_type"],
                file_type="document",
            )
            return Response(result, status=status.HTTP_200_OK)
        from apps.documents.services import VersionControlService
        new_doc = VersionControlService.create_new_version(
            existing_document=old_doc,
            file_key=request.data["file_key"],
            file_name=serializer.validated_data["file_name"],
            file_size=request.data.get("file_size", 0),
            content_type=serializer.validated_data["content_type"],
            uploaded_by=request.user,
        )
        return Response(DocumentDetailSerializer(new_doc).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Return a presigned S3 download URL."""
        doc = self.get_object()
        if not doc.file_key:
            return Response({"detail": "No file attached."}, status=status.HTTP_404_NOT_FOUND)
        from apps.documents.services import FileUploadService
        try:
            url = FileUploadService.generate_download_url(doc.file_key, doc.file_name)
            return Response({"download_url": url, "file_name": doc.file_name})
        except Exception as exc:
            logger.error("download URL error for doc %s: %s", pk, exc)
            return Response({"detail": "Failed to generate download URL."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge(self, request, pk=None):
        """Record that the current user has acknowledged this document."""
        doc = self.get_object()
        ack, created = DocumentAcknowledgment.objects.get_or_create(document=doc, user=request.user)
        data = DocumentAcknowledgmentSerializer(ack).data
        return Response(data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        """List all versions of a document."""
        current = self.get_object()
        from apps.documents.services import VersionControlService
        history = VersionControlService.get_version_history(current)
        return Response(DocumentListSerializer(history, many=True, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="acknowledgments")
    def acknowledgments(self, request, pk=None):
        """List all acknowledgments for a document."""
        doc = self.get_object()
        acks = DocumentAcknowledgment.objects.filter(document=doc).select_related("user")
        return Response(DocumentAcknowledgmentSerializer(acks, many=True).data)


# ---------------------------------------------------------------------------
# RFI
# ---------------------------------------------------------------------------

class RFIViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for RFIs. rfi_number auto-increments per project."""
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "priority", "assigned_to"]
    search_fields = ["subject", "question"]
    ordering_fields = ["created_at", "due_date", "priority", "rfi_number"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return RFI.objects.select_related(
            "project", "requested_by", "assigned_to"
        ).prefetch_related("distribution_list")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return RFICreateSerializer
        if self.action == "retrieve":
            return RFIDetailSerializer
        return RFIListSerializer

    def perform_create(self, serializer):
        from apps.documents.services import RFIService
        org = self.request.current_organization
        project = serializer.validated_data["project"]
        rfi_number = RFIService.get_next_rfi_number(project)
        serializer.save(
            organization=org,
            rfi_number=rfi_number,
            requested_by=self.request.user,
            status=RFI.Status.OPEN,
        )

    @action(detail=True, methods=["post"], url_path="answer")
    def answer(self, request, pk=None):
        """Record an answer, changes status to ANSWERED."""
        rfi = self.get_object()
        if rfi.status == RFI.Status.CLOSED:
            return Response({"detail": "Cannot answer a closed RFI."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RFIAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.documents.services import RFIService
        updated = RFIService.answer_rfi(
            rfi=rfi,
            answer_text=serializer.validated_data["answer"],
            answered_by=request.user,
        )
        if serializer.validated_data.get("cost_impact") is not None:
            updated.cost_impact = serializer.validated_data["cost_impact"]
        if serializer.validated_data.get("schedule_impact_days") is not None:
            updated.schedule_impact_days = serializer.validated_data["schedule_impact_days"]
        updated.save(update_fields=["cost_impact", "schedule_impact_days"])
        return Response(RFIDetailSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        """Close an RFI."""
        rfi = self.get_object()
        if rfi.status == RFI.Status.CLOSED:
            return Response({"detail": "RFI already closed."}, status=status.HTTP_400_BAD_REQUEST)
        from apps.documents.services import RFIService
        updated = RFIService.close_rfi(rfi=rfi, closed_by=request.user)
        return Response(RFIDetailSerializer(updated).data)

    @action(detail=True, methods=["post"], url_path="distribute")
    def distribute(self, request, pk=None):
        """Update distribution list. Expects: {"user_ids": [...]}"""
        rfi = self.get_object()
        user_ids = request.data.get("user_ids", [])
        if not isinstance(user_ids, list):
            return Response({"detail": "user_ids must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        rfi.distribution_list.set(User.objects.filter(pk__in=user_ids))
        return Response({"distribution_count": rfi.distribution_list.count()})


# ---------------------------------------------------------------------------
# Submittal
# ---------------------------------------------------------------------------

class SubmittalViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for submittals. submittal_number auto-increments per project."""
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "status", "reviewer"]
    search_fields = ["title", "spec_section"]
    ordering_fields = ["created_at", "due_date", "submittal_number"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Submittal.objects.select_related(
            "project", "submitted_by", "reviewer"
        ).prefetch_related("documents")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return SubmittalCreateSerializer
        if self.action == "retrieve":
            return SubmittalDetailSerializer
        return SubmittalListSerializer

    def perform_create(self, serializer):
        from django.db.models import Max
        org = self.request.current_organization
        project = serializer.validated_data["project"]
        max_num = Submittal.objects.filter(project=project).aggregate(
            Max("submittal_number")
        )["submittal_number__max"]
        serializer.save(
            organization=org,
            submittal_number=(max_num or 0) + 1,
            submitted_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        """Move DRAFT to SUBMITTED."""
        submittal = self.get_object()
        if submittal.status != Submittal.Status.DRAFT:
            return Response({"detail": "Only draft submittals can be submitted."}, status=status.HTTP_400_BAD_REQUEST)
        submittal.status = Submittal.Status.SUBMITTED
        submittal.save(update_fields=["status"])
        return Response(SubmittalDetailSerializer(submittal).data)

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        """Record review decision."""
        submittal = self.get_object()
        if submittal.status not in (Submittal.Status.SUBMITTED, Submittal.Status.DRAFT):
            return Response({"detail": "Submittal has already been reviewed."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubmittalReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submittal.status = serializer.validated_data["status"]
        submittal.review_notes = serializer.validated_data.get("review_notes", "")
        submittal.reviewed_at = timezone.now()
        submittal.reviewer = request.user
        submittal.save(update_fields=["status", "review_notes", "reviewed_at", "reviewer"])
        return Response(SubmittalDetailSerializer(submittal).data)


# ---------------------------------------------------------------------------
# Photo
# ---------------------------------------------------------------------------

class PhotoViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """
    CRUD for project photos.

    Upload flow:
      1. POST /bulk-upload-urls/  - get presigned PUT URLs
      2. Client PUTs files to S3
      3. POST /bulk-create/       - create Photo records
    """
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "category", "is_client_visible", "phase"]
    search_fields = ["caption", "file_name", "phase"]
    ordering_fields = ["taken_at", "created_at", "category"]
    ordering = ["-taken_at", "-created_at"]

    def get_queryset(self):
        return Photo.objects.select_related("project", "uploaded_by", "linked_daily_log")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PhotoDetailSerializer
        return PhotoListSerializer

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use POST /bulk-upload-urls/ then POST /bulk-create/."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["post"], url_path="upload-url")
    def upload_url(self, request):
        """Get presigned upload URL for a single photo."""
        from apps.documents.services import FileUploadService
        org = request.current_organization
        try:
            result = FileUploadService.generate_upload_url(
                organization_id=str(org.id),
                project_id=request.data.get("project"),
                file_name=request.data.get("file_name", "photo.jpg"),
                content_type=request.data.get("content_type", "image/jpeg"),
                file_type="photo",
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.error("photo upload_url error: %s", exc)
            return Response({"detail": "Failed to generate upload URL."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=["post"], url_path="bulk-upload-urls")
    def bulk_upload_urls(self, request):
        """Request presigned PUT URLs for multiple photos at once."""
        serializer = BulkPhotoUploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.documents.services import FileUploadService
        org = request.current_organization
        try:
            results = FileUploadService.generate_bulk_upload_urls(
                organization_id=str(org.id),
                project_id=str(serializer.validated_data["project"]),
                files=serializer.validated_data["files"],
            )
            return Response({"urls": results}, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.error("bulk_upload_urls error: %s", exc)
            return Response({"detail": "Failed to generate upload URLs."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Create multiple Photo records after files have been uploaded to S3."""
        photos_data = request.data.get("photos", [])
        if not isinstance(photos_data, list) or not photos_data:
            return Response({"detail": "photos must be a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

        org = request.current_organization
        created_photos = []
        errors = []

        for i, photo_data in enumerate(photos_data):
            s = PhotoCreateSerializer(data=photo_data)
            if not s.is_valid():
                errors.append({"index": i, "errors": s.errors})
                continue
            data = s.validated_data
            from apps.projects.models import Project
            try:
                project = Project.objects.get(pk=data["project"], organization=org)
            except Project.DoesNotExist:
                errors.append({"index": i, "errors": {"project": "Not found."}})
                continue

            photo = Photo.objects.create(
                organization=org,
                project=project,
                file_key=data["file_key"],
                thumbnail_key=data.get("thumbnail_key", ""),
                file_name=data["file_name"],
                file_size=data["file_size"],
                content_type=data.get("content_type", "image/jpeg"),
                caption=data.get("caption", ""),
                category=data.get("category", Photo.Category.PROGRESS),
                phase=data.get("phase", ""),
                is_client_visible=data.get("is_client_visible", True),
                taken_at=data.get("taken_at"),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                uploaded_by=request.user,
            )
            created_photos.append(photo)
            if not data.get("thumbnail_key"):
                try:
                    from apps.documents.tasks import generate_thumbnails
                    generate_thumbnails.delay(str(photo.id))
                except Exception:
                    pass

        result = PhotoListSerializer(created_photos, many=True, context={"request": request}).data
        response_data = {"created": result}
        if errors:
            response_data["errors"] = errors
        return Response(
            response_data,
            status=status.HTTP_201_CREATED if created_photos else status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post"], url_path="annotate")
    def annotate(self, request, pk=None):
        """Save canvas annotation markup."""
        photo = self.get_object()
        serializer = PhotoAnnotateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo.annotations = serializer.validated_data["annotations"]
        photo.save(update_fields=["annotations"])
        return Response(PhotoDetailSerializer(photo, context={"request": request}).data)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """Return a presigned download URL for the photo."""
        photo = self.get_object()
        from apps.documents.services import FileUploadService
        try:
            url = FileUploadService.generate_download_url(photo.file_key, photo.file_name)
            return Response({"download_url": url, "file_name": photo.file_name})
        except Exception as exc:
            logger.error("photo download URL error for %s: %s", pk, exc)
            return Response({"detail": "Failed to generate download URL."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ---------------------------------------------------------------------------
# PhotoAlbum
# ---------------------------------------------------------------------------

class PhotoAlbumViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for curated or auto-generated photo albums."""
    permission_classes = [IsOrganizationMember]
    filterset_fields = ["project", "is_auto_generated"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return PhotoAlbum.objects.select_related("project", "cover_photo").prefetch_related("photos")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PhotoAlbumCreateSerializer
        if self.action == "retrieve":
            return PhotoAlbumDetailSerializer
        return PhotoAlbumListSerializer

    def perform_create(self, serializer):
        serializer.save(organization=self.request.current_organization)

    @action(detail=True, methods=["post"], url_path="add-photos")
    def add_photos(self, request, pk=None):
        """Add photos to album. Expects: {"photo_ids": [...]}"""
        album = self.get_object()
        photo_ids = request.data.get("photo_ids", [])
        if not isinstance(photo_ids, list):
            return Response({"detail": "photo_ids must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        album.photos.add(*Photo.objects.filter(pk__in=photo_ids, organization=request.current_organization))
        return Response({"photo_count": album.photos.count()})

    @action(detail=True, methods=["post"], url_path="remove-photos")
    def remove_photos(self, request, pk=None):
        """Remove photos from album. Expects: {"photo_ids": [...]}"""
        album = self.get_object()
        photo_ids = request.data.get("photo_ids", [])
        if not isinstance(photo_ids, list):
            return Response({"detail": "photo_ids must be a list."}, status=status.HTTP_400_BAD_REQUEST)
        album.photos.remove(*Photo.objects.filter(pk__in=photo_ids, organization=request.current_organization))
        return Response({"photo_count": album.photos.count()})

    @action(detail=True, methods=["post"], url_path="set-cover")
    def set_cover(self, request, pk=None):
        """Set a photo as the album cover."""
        album = self.get_object()
        photo_id = request.data.get("photo_id")
        if not photo_id:
            return Response({"detail": "photo_id required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            photo = Photo.objects.get(pk=photo_id, organization=request.current_organization)
        except Photo.DoesNotExist:
            return Response({"detail": "Photo not found."}, status=status.HTTP_404_NOT_FOUND)
        album.cover_photo = photo
        album.save(update_fields=["cover_photo"])
        return Response(PhotoAlbumDetailSerializer(album, context={"request": request}).data)
