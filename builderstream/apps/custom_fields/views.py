from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsOrganizationAdmin, IsOrganizationMember
from apps.core.mixins import TenantViewSetMixin

from apps.custom_fields.models import CustomFieldDefinition
from apps.custom_fields.serializers import (
    CustomFieldDefinitionListSerializer,
    CustomFieldDefinitionSerializer,
)
from apps.custom_fields.services import CustomFieldService


class CustomFieldDefinitionViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for custom field definitions.

    List / retrieve: any org member.
    Create / update / delete: admin or owner only.
    """

    queryset = CustomFieldDefinition.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CustomFieldDefinitionListSerializer
        return CustomFieldDefinitionSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve", "for_model"):
            return [IsOrganizationMember()]
        return [IsOrganizationAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        model_name = self.request.query_params.get("model_name")
        if model_name:
            qs = qs.filter(model_name=model_name)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs.order_by("model_name", "sort_order", "label")

    def perform_create(self, serializer):
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        serializer.save(organization=org)

    @action(detail=False, methods=["get"], url_path="for-model/(?P<model_name>[^/.]+)")
    def for_model(self, request, model_name: str = ""):
        """GET /custom-fields/definitions/for-model/{model_name}/
        Returns active field definitions for the given model.
        """
        from apps.tenants.context import get_current_organization
        org = get_current_organization()
        fields = CustomFieldService.get_fields_for_model(org, model_name)
        serializer = CustomFieldDefinitionSerializer(fields, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="reorder")
    def reorder(self, request, pk=None):
        """POST /custom-fields/definitions/{pk}/reorder/ — update sort_order."""
        field_def = self.get_object()
        sort_order = request.data.get("sort_order")
        if sort_order is None:
            return Response(
                {"detail": "sort_order is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        field_def.sort_order = int(sort_order)
        field_def.save(update_fields=["sort_order"])
        return Response({"sort_order": field_def.sort_order})
