"""Teams ViewSet."""
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.mixins import TenantViewSetMixin
from apps.core.permissions import IsOrganizationAdmin

from .models import Team, TeamMember
from .serializers import (
    AddMemberSerializer,
    TeamListSerializer,
    TeamMemberSerializer,
    TeamSerializer,
)

User = get_user_model()


class TeamViewSet(TenantViewSetMixin, viewsets.ModelViewSet):
    """CRUD for teams + add/remove members."""

    queryset = Team.objects.prefetch_related("members__user")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return TeamSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "add_member", "remove_member"):
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        """Add a user to a team (or update their role if already a member)."""
        team = self.get_object()
        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        role = serializer.validated_data["role"]

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        member, created = TeamMember.objects.get_or_create(
            team=team,
            user=user,
            defaults={"role": role},
        )
        if not created:
            member.role = role
            member.save(update_fields=["role", "updated_at"])

        return Response(
            TeamMemberSerializer(member).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["delete"], url_path=r"remove-member/(?P<user_id>[^/.]+)")
    def remove_member(self, request, pk=None, user_id=None):
        """Remove a user from a team."""
        team = self.get_object()
        deleted, _ = TeamMember.objects.filter(team=team, user_id=user_id).delete()
        if not deleted:
            return Response({"detail": "Member not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
