"""Tenant views."""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsOrganizationAdmin, IsOrganizationOwner

from .models import ActiveModule, Organization, OrganizationMembership
from .serializers import (
    InviteMemberSerializer,
    ModuleActivationSerializer,
    OrganizationMembershipSerializer,
    OrganizationSerializer,
)

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    """CRUD for organizations.

    - Any authenticated user can create an org (becomes OWNER automatically).
    - Only OWNER/ADMIN can update.
    - Members can retrieve their own orgs.
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        """Only return organizations the user belongs to."""
        if self.request.user.is_staff:
            return Organization.objects.all()
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
        ).distinct()

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Auto-assign the creating user as OWNER.

        The post_save signal handles membership creation, default module
        activation, and Stripe customer setup.
        """
        serializer.save(owner=self.request.user)


class MembershipViewSet(viewsets.ModelViewSet):
    """Manage organization memberships.

    - List members of the current organization.
    - Invite new members (sends email placeholder).
    - Update roles, deactivate members.
    - Enforces max_users limit from subscription.
    """

    queryset = OrganizationMembership.objects.select_related("user", "organization")
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        if org:
            return self.queryset.filter(organization=org)
        return self.queryset.none()

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy", "invite"):
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["post"])
    def invite(self, request):
        """Invite a new member by email."""
        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        org = request.organization
        if not org:
            return Response(
                {"detail": "No active organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enforce max_users
        current_count = org.memberships.filter(is_active=True).count()
        if current_count >= org.max_users:
            return Response(
                {"detail": f"Organization has reached the maximum of {org.max_users} users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]

        # Find or note the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # In production, send an invitation email here
            return Response(
                {"detail": f"Invitation will be sent to {email}."},
                status=status.HTTP_202_ACCEPTED,
            )

        # Check for existing membership
        membership, created = OrganizationMembership.objects.get_or_create(
            user=user,
            organization=org,
            defaults={
                "role": role,
                "invited_by": request.user,
                "invited_at": timezone.now(),
            },
        )

        if not created:
            if membership.is_active:
                return Response(
                    {"detail": "User is already a member of this organization."},
                    status=status.HTTP_409_CONFLICT,
                )
            # Reactivate
            membership.is_active = True
            membership.role = role
            membership.invited_by = request.user
            membership.invited_at = timezone.now()
            membership.save()

        return Response(
            OrganizationMembershipSerializer(membership).data,
            status=status.HTTP_201_CREATED,
        )


class ModuleViewSet(viewsets.ModelViewSet):
    """List and manage active modules for the organization."""

    queryset = ActiveModule.objects.all()
    serializer_class = ModuleActivationSerializer
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        org = getattr(self.request, "organization", None)
        if org:
            return self.queryset.filter(organization=org)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)

    def perform_update(self, serializer):
        instance = self.get_object()
        # Prevent deactivating always-active modules
        if instance.module_key in ActiveModule.ALWAYS_ACTIVE:
            serializer.validated_data["is_active"] = True
        serializer.save()


class SwitchOrganizationView(APIView):
    """Allow users to switch their active organization context."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        org_id = request.data.get("organization_id")
        if not org_id:
            return Response(
                {"detail": "organization_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate membership
        try:
            membership = OrganizationMembership.objects.select_related("organization").get(
                user=request.user,
                organization_id=org_id,
                is_active=True,
            )
        except OrganizationMembership.DoesNotExist:
            return Response(
                {"detail": "You are not a member of this organization."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not membership.organization.is_active:
            return Response(
                {"detail": "This organization is no longer active."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update user's last active organization
        request.user.last_active_organization = membership.organization
        request.user.save(update_fields=["last_active_organization"])

        return Response(
            {"detail": "Switched organization.", "organization": OrganizationSerializer(membership.organization).data},
            status=status.HTTP_200_OK,
        )
