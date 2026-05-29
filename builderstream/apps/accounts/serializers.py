"""Account serializers for auth, registration, and profile management."""
import re
import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone as tz
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.tenants.models import Organization, OrganizationMembership

User = get_user_model()


# ---------------------------------------------------------------------------
# Helper: lightweight membership + org info for nesting in responses
# ---------------------------------------------------------------------------

class OrganizationMembershipSummarySerializer(serializers.ModelSerializer):
    organization_id = serializers.UUIDField(source="organization.id")
    organization_name = serializers.CharField(source="organization.name")
    organization_slug = serializers.SlugField(source="organization.slug")

    class Meta:
        model = OrganizationMembership
        fields = [
            "organization_id",
            "organization_name",
            "organization_slug",
            "role",
            "is_active",
        ]


# ---------------------------------------------------------------------------
# Password strength helpers
# ---------------------------------------------------------------------------

def _validate_password_strength(value):
    """Enforce 8+ chars, 1 uppercase, 1 number."""
    if not re.search(r"[A-Z]", value):
        raise serializers.ValidationError(
            "Must contain at least one uppercase letter."
        )
    if not re.search(r"\d", value):
        raise serializers.ValidationError(
            "Must contain at least one number."
        )
    return value


# ---------------------------------------------------------------------------
# 1. RegisterSerializer
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    company_name = serializers.CharField(max_length=200)
    industry_type = serializers.ChoiceField(
        choices=Organization.IndustryType.choices,
        required=False,
        allow_blank=True,
    )

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return email

    def validate_password(self, value):
        return _validate_password_strength(value)

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password_confirm")
        company_name = validated_data.pop("company_name")
        industry_type = validated_data.pop("industry_type", "")
        password = validated_data.pop("password")

        # 1. Create user
        user = User.objects.create_user(
            email=validated_data["email"],
            password=password,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data.get("phone", ""),
            email_verification_token=uuid.uuid4(),
        )

        # 2. Create organization (signal auto-creates OWNER membership + modules)
        base_slug = slugify(company_name)
        slug = base_slug or "org"
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        Organization.objects.create(
            name=company_name,
            slug=slug,
            owner=user,
            industry_type=industry_type,
        )

        # 3. Set user's last active org (reload to get org from signal)
        membership = OrganizationMembership.objects.filter(user=user).first()
        if membership:
            user.last_active_organization = membership.organization
            user.save(update_fields=["last_active_organization"])

        # 4. Send verification email (async)
        from apps.accounts.tasks import send_verification_email

        send_verification_email.delay(str(user.id))

        return user


# ---------------------------------------------------------------------------
# 2. CustomTokenObtainPairSerializer (Login)
# ---------------------------------------------------------------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        data["user"] = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar": user.avatar.url if user.avatar else None,
            "job_title": user.job_title,
            "email_verified": user.email_verified,
            "timezone": user.timezone,
            "last_active_organization": (
                str(user.last_active_organization_id)
                if user.last_active_organization_id
                else None
            ),
        }

        # Add organizations list
        memberships = OrganizationMembership.objects.filter(
            user=user, is_active=True
        ).select_related("organization")
        data["organizations"] = OrganizationMembershipSummarySerializer(
            memberships, many=True
        ).data

        if not user.email_verified:
            data["warning"] = (
                "Email not yet verified. Some features may be restricted."
            )

        return data


# ---------------------------------------------------------------------------
# 3. UserProfileSerializer
# ---------------------------------------------------------------------------

class UserProfileSerializer(serializers.ModelSerializer):
    organizations = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "job_title",
            "timezone",
            "notification_preferences",
            "email_verified",
            "last_active_organization",
            "date_joined",
            "last_login",
            "organizations",
        ]
        read_only_fields = [
            "id",
            "email",
            "email_verified",
            "date_joined",
            "last_login",
        ]

    def get_organizations(self, obj):
        memberships = (
            obj.memberships.filter(is_active=True)
            .select_related("organization")
        )
        return OrganizationMembershipSummarySerializer(
            memberships, many=True
        ).data


# ---------------------------------------------------------------------------
# 4. ChangePasswordSerializer
# ---------------------------------------------------------------------------

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_new_password(self, value):
        return _validate_password_strength(value)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


# ---------------------------------------------------------------------------
# 5. ForgotPasswordSerializer
# ---------------------------------------------------------------------------

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


# ---------------------------------------------------------------------------
# 6. ResetPasswordSerializer
# ---------------------------------------------------------------------------

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8)

    def validate_new_password(self, value):
        return _validate_password_strength(value)


# ---------------------------------------------------------------------------
# 7. InviteAcceptSerializer
# ---------------------------------------------------------------------------

class InviteAcceptSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate_token(self, value):
        try:
            membership = OrganizationMembership.objects.select_related(
                "organization", "user"
            ).get(invitation_token=value, is_active=False)
        except OrganizationMembership.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid or expired invitation token."
            )
        self._membership = membership
        return value

    def validate_password(self, value):
        return _validate_password_strength(value)

    @transaction.atomic
    def create(self, validated_data):
        membership = self._membership

        if not membership.user_id:
            raise serializers.ValidationError("Invalid invitation state.")

        # Update user details
        user = membership.user
        user.first_name = validated_data["first_name"]
        user.last_name = validated_data["last_name"]
        user.set_password(validated_data["password"])
        user.email_verified = True
        user.save(update_fields=[
            "first_name", "last_name", "password", "email_verified",
        ])

        # Activate membership and invalidate token
        membership.is_active = True
        membership.accepted_at = tz.now()
        membership.invitation_token = None
        membership.save(update_fields=[
            "is_active", "accepted_at", "invitation_token",
        ])

        return user
