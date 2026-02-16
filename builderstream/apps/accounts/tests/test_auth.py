"""Comprehensive auth test suite for Section 3: Authentication & Registration."""
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.tenants.models import Organization, OrganizationMembership

User = get_user_model()

REGISTER_URL = "/api/v1/auth/register/"
LOGIN_URL = "/api/v1/auth/login/"
VERIFY_EMAIL_URL = "/api/v1/auth/verify-email/"
RESEND_VERIFICATION_URL = "/api/v1/auth/resend-verification/"
FORGOT_PASSWORD_URL = "/api/v1/auth/forgot-password/"
RESET_PASSWORD_URL = "/api/v1/auth/reset-password/"
CHANGE_PASSWORD_URL = "/api/v1/auth/change-password/"
PROFILE_URL = "/api/v1/users/me/"
USER_ORGS_URL = "/api/v1/users/me/organizations/"
INVITE_ACCEPT_URL = "/api/v1/auth/invite/accept/"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "testuser@example.com",
        "password": "TestPass1!",
        "password_confirm": "TestPass1!",
        "first_name": "Test",
        "last_name": "User",
        "company_name": "Test Company",
    }


@pytest.fixture
def create_user(db):
    def _create_user(email="existing@example.com", password="TestPass1!", **kwargs):
        defaults = {
            "first_name": "Existing",
            "last_name": "User",
            "email_verified": True,
        }
        defaults.update(kwargs)
        return User.objects.create_user(email=email, password=password, **defaults)

    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user


# ======================================================================
# Registration Tests
# ======================================================================


@pytest.fixture(autouse=True)
def _disable_throttling(settings, monkeypatch):
    """Disable DRF throttling for all tests."""
    from apps.accounts.views import RegisterView

    monkeypatch.setattr(RegisterView, "throttle_classes", [])


@pytest.mark.django_db
class TestRegistration:
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_register_creates_user_and_org(self, api_client, user_data):
        response = api_client.post(REGISTER_URL, user_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["first_name"] == "Test"
        assert data["user"]["email_verified"] is False

        # User created with UUID PK
        user = User.objects.get(email=user_data["email"])
        assert isinstance(user.id, uuid.UUID)

        # Organization created
        org = Organization.objects.get(owner=user)
        assert org.name == "Test Company"

        # OWNER membership created (by signal)
        membership = OrganizationMembership.objects.get(user=user, organization=org)
        assert membership.role == OrganizationMembership.Role.OWNER
        assert membership.is_active is True

    def test_register_duplicate_email(self, api_client, user_data, create_user):
        create_user(email=user_data["email"])
        response = api_client.post(REGISTER_URL, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch(self, api_client, user_data):
        user_data["password_confirm"] = "DifferentPass1!"
        response = api_client.post(REGISTER_URL, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password_no_uppercase(self, api_client, user_data):
        user_data["password"] = "weakpass1"
        user_data["password_confirm"] = "weakpass1"
        response = api_client.post(REGISTER_URL, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password_no_number(self, api_client, user_data):
        user_data["password"] = "WeakPasss"
        user_data["password_confirm"] = "WeakPasss"
        response = api_client.post(REGISTER_URL, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client, user_data):
        user_data["password"] = "Sh1!"
        user_data["password_confirm"] = "Sh1!"
        response = api_client.post(REGISTER_URL, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_required_fields(self, api_client):
        response = api_client.post(REGISTER_URL, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ======================================================================
# Login Tests
# ======================================================================


@pytest.mark.django_db
class TestLogin:
    def test_login_returns_tokens_and_profile(self, api_client, create_user):
        user = create_user(email="login@example.com")
        response = api_client.post(
            LOGIN_URL,
            {"email": "login@example.com", "password": "TestPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert data["user"]["email"] == "login@example.com"
        assert "organizations" in data

    def test_login_unverified_email_warning(self, api_client, create_user):
        create_user(email="unverified@example.com", email_verified=False)
        response = api_client.post(
            LOGIN_URL,
            {"email": "unverified@example.com", "password": "TestPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "warning" in data

    def test_login_wrong_password(self, api_client, create_user):
        create_user(email="wrong@example.com")
        response = api_client.post(
            LOGIN_URL,
            {"email": "wrong@example.com", "password": "WrongPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_email(self, api_client):
        response = api_client.post(
            LOGIN_URL,
            {"email": "nobody@example.com", "password": "TestPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ======================================================================
# Email Verification Tests
# ======================================================================


@pytest.mark.django_db
class TestEmailVerification:
    def test_verify_email_valid_token(self, api_client, create_user):
        token = uuid.uuid4()
        user = create_user(
            email="verify@example.com",
            email_verified=False,
            email_verification_token=token,
        )
        response = api_client.get(VERIFY_EMAIL_URL, {"token": str(token)})
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.email_verified is True
        assert user.email_verification_token is None

    def test_verify_email_invalid_token(self, api_client):
        response = api_client.get(VERIFY_EMAIL_URL, {"token": str(uuid.uuid4())})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_email_no_token(self, api_client):
        response = api_client.get(VERIFY_EMAIL_URL)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_resend_verification(self, authenticated_client):
        client, user = authenticated_client
        user.email_verified = False
        user.save(update_fields=["email_verified"])

        response = client.post(RESEND_VERIFICATION_URL)
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.email_verification_token is not None

    def test_resend_verification_already_verified(self, authenticated_client):
        client, user = authenticated_client
        response = client.post(RESEND_VERIFICATION_URL)
        assert response.status_code == status.HTTP_200_OK
        assert "already verified" in response.json()["detail"].lower()


# ======================================================================
# Profile Tests
# ======================================================================


@pytest.mark.django_db
class TestProfile:
    def test_get_profile(self, authenticated_client):
        client, user = authenticated_client
        response = client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert "organizations" in data

    def test_update_profile(self, authenticated_client):
        client, user = authenticated_client
        response = client.patch(
            PROFILE_URL,
            {"first_name": "Updated", "job_title": "Developer"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated"
        assert user.job_title == "Developer"

    def test_profile_unauthenticated(self, api_client):
        response = api_client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_email_readonly(self, authenticated_client):
        client, user = authenticated_client
        original_email = user.email
        response = client.patch(
            PROFILE_URL,
            {"email": "newemail@example.com"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == original_email


# ======================================================================
# Password Reset Tests
# ======================================================================


@pytest.mark.django_db
class TestPasswordReset:
    def test_forgot_password_existing_email(self, api_client, create_user):
        create_user(email="reset@example.com")
        response = api_client.post(
            FORGOT_PASSWORD_URL,
            {"email": "reset@example.com"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "sent" in response.json()["detail"].lower()

    def test_forgot_password_nonexistent_email(self, api_client):
        response = api_client.post(
            FORGOT_PASSWORD_URL,
            {"email": "nobody@example.com"},
            format="json",
        )
        # Never reveals whether email exists
        assert response.status_code == status.HTTP_200_OK

    def test_reset_password_with_valid_token(self, api_client, create_user):
        user = create_user(email="resetme@example.com")
        reset_token = uuid.uuid4()
        cache.set(f"password_reset_{reset_token}", str(user.id), timeout=86400)

        response = api_client.post(
            RESET_PASSWORD_URL,
            {"token": str(reset_token), "new_password": "NewPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify password changed
        user.refresh_from_db()
        assert user.check_password("NewPass1!")

        # Token consumed
        assert cache.get(f"password_reset_{reset_token}") is None

    def test_reset_password_invalid_token(self, api_client):
        response = api_client.post(
            RESET_PASSWORD_URL,
            {"token": str(uuid.uuid4()), "new_password": "NewPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password(self, authenticated_client):
        client, user = authenticated_client
        response = client.post(
            CHANGE_PASSWORD_URL,
            {"old_password": "TestPass1!", "new_password": "NewPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.check_password("NewPass1!")

    def test_change_password_wrong_old(self, authenticated_client):
        client, _ = authenticated_client
        response = client.post(
            CHANGE_PASSWORD_URL,
            {"old_password": "WrongOld1!", "new_password": "NewPass1!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ======================================================================
# Role-Based Permission Tests
# ======================================================================


@pytest.mark.django_db
class TestRolePermissions:
    def test_role_hierarchy(self):
        from apps.core.permissions import ROLE_HIERARCHY

        assert ROLE_HIERARCHY["owner"] > ROLE_HIERARCHY["admin"]
        assert ROLE_HIERARCHY["admin"] > ROLE_HIERARCHY["project_manager"]
        assert ROLE_HIERARCHY["project_manager"] > ROLE_HIERARCHY["estimator"]
        assert ROLE_HIERARCHY["estimator"] > ROLE_HIERARCHY["accountant"]
        assert ROLE_HIERARCHY["accountant"] > ROLE_HIERARCHY["field_worker"]
        assert ROLE_HIERARCHY["field_worker"] > ROLE_HIERARCHY["read_only"]

    def test_role_required_factory(self):
        from apps.core.permissions import role_required

        perm_class = role_required("project_manager")
        assert perm_class.__name__ == "RoleRequired_project_manager"


# ======================================================================
# Invitation Accept Tests
# ======================================================================


@pytest.mark.django_db
class TestInvitationAccept:
    def test_accept_invitation(self, api_client, create_user, db):
        # Create org and invite
        owner = create_user(email="owner@example.com")
        org = Organization.objects.create(
            name="Test Org", slug="test-org-invite", owner=owner
        )
        invitee = User.objects.create_user(
            email="invitee@example.com",
            password=None,
            first_name="",
            last_name="",
        )
        invite_token = uuid.uuid4()
        membership = OrganizationMembership.objects.create(
            user=invitee,
            organization=org,
            role=OrganizationMembership.Role.PROJECT_MANAGER,
            is_active=False,
            invitation_token=invite_token,
        )

        response = api_client.post(
            INVITE_ACCEPT_URL,
            {
                "token": str(invite_token),
                "password": "InvitePass1!",
                "first_name": "Invited",
                "last_name": "User",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert data["user"]["first_name"] == "Invited"

        # Membership activated
        membership.refresh_from_db()
        assert membership.is_active is True
        assert membership.invitation_token is None
        assert membership.accepted_at is not None

        # User details updated
        invitee.refresh_from_db()
        assert invitee.first_name == "Invited"
        assert invitee.email_verified is True
        assert invitee.check_password("InvitePass1!")

    def test_accept_invalid_token(self, api_client):
        response = api_client.post(
            INVITE_ACCEPT_URL,
            {
                "token": str(uuid.uuid4()),
                "password": "InvitePass1!",
                "first_name": "Nobody",
                "last_name": "User",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ======================================================================
# User Organizations Tests
# ======================================================================


@pytest.mark.django_db
class TestUserOrganizations:
    def test_list_user_organizations(self, authenticated_client):
        client, user = authenticated_client
        # Signal auto-creates OWNER membership when org is created
        Organization.objects.create(
            name="My Org", slug="my-org-test", owner=user
        )

        response = client.get(USER_ORGS_URL)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Handle paginated or non-paginated response
        results = data.get("results", data) if isinstance(data, dict) else data
        assert len(results) >= 1
        org_names = [d["organization_name"] for d in results]
        assert "My Org" in org_names

    def test_list_organizations_unauthenticated(self, api_client):
        response = api_client.get(USER_ORGS_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ======================================================================
# Custom User Model Tests
# ======================================================================


@pytest.mark.django_db
class TestCustomUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email="model@example.com",
            password="TestPass1!",
            first_name="Model",
            last_name="Test",
        )
        assert user.email == "model@example.com"
        assert isinstance(user.id, uuid.UUID)
        assert user.is_active is True
        assert user.is_staff is False
        assert user.check_password("TestPass1!")

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="super@example.com",
            password="SuperPass1!",
            first_name="Super",
            last_name="User",
        )
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.email_verified is True

    def test_email_normalized_lowercase(self):
        user = User.objects.create_user(
            email="MiXeD@EXAMPLE.COM",
            password="TestPass1!",
            first_name="Mixed",
            last_name="Case",
        )
        assert user.email == "mixed@example.com"

    def test_create_user_no_email(self):
        with pytest.raises(ValueError, match="Email"):
            User.objects.create_user(
                email="",
                password="TestPass1!",
                first_name="No",
                last_name="Email",
            )

    def test_get_full_name(self):
        user = User(first_name="John", last_name="Doe")
        assert user.get_full_name() == "John Doe"

    def test_str_representation(self):
        user = User(email="str@example.com")
        assert str(user) == "str@example.com"
