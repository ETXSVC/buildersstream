"""Account views for authentication, registration, and profile management."""
import uuid

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.tenants.models import OrganizationMembership

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    InviteAcceptSerializer,
    OrganizationMembershipSummarySerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserProfileSerializer,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class RegistrationRateThrottle(AnonRateThrottle):
    rate = "5/hour"


# ---------------------------------------------------------------------------
# 1. RegisterView
# ---------------------------------------------------------------------------

class RegisterView(APIView):
    """POST: Create user + org + membership, send verification email, return JWT."""

    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email_verified": user.email_verified,
                },
                "message": "Registration successful. Please verify your email.",
            },
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# 2. LoginView
# ---------------------------------------------------------------------------

class LoginView(TokenObtainPairView):
    """POST: Authenticate and return JWT + user profile + organizations."""

    serializer_class = CustomTokenObtainPairSerializer


# ---------------------------------------------------------------------------
# 3. VerifyEmailView
# ---------------------------------------------------------------------------

class VerifyEmailView(APIView):
    """GET: Verify email with token from query params."""

    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"detail": "Verification token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email_verification_token=token)
        except (User.DoesNotExist, ValueError):
            return Response(
                {"detail": "Invalid or expired verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.email_verified = True
        user.email_verification_token = None
        user.save(update_fields=["email_verified", "email_verification_token"])

        return Response({"detail": "Email verified successfully."})


# ---------------------------------------------------------------------------
# 4. ResendVerificationView
# ---------------------------------------------------------------------------

class ResendVerificationView(APIView):
    """POST: Resend the email verification link."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response({"detail": "Email is already verified."})

        user.email_verification_token = uuid.uuid4()
        user.save(update_fields=["email_verification_token"])

        from .tasks import send_verification_email

        send_verification_email.delay(str(user.id))

        return Response({"detail": "Verification email sent."})


# ---------------------------------------------------------------------------
# 5. ProfileView
# ---------------------------------------------------------------------------

class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH: Current user profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ---------------------------------------------------------------------------
# 6. ChangePasswordView
# ---------------------------------------------------------------------------

class ChangePasswordView(APIView):
    """POST: Change password (requires old password)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password changed successfully."})


# ---------------------------------------------------------------------------
# 7. ForgotPasswordView
# ---------------------------------------------------------------------------

class ForgotPasswordView(APIView):
    """POST: Send password reset email (never reveals if email exists)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            reset_token = uuid.uuid4()
            cache.set(
                f"password_reset_{reset_token}",
                str(user.id),
                timeout=86400,  # 24 hours
            )

            from .tasks import send_password_reset_email

            send_password_reset_email.delay(str(user.id), str(reset_token))

        return Response(
            {"detail": "If an account with that email exists, a reset link has been sent."}
        )


# ---------------------------------------------------------------------------
# 8. ResetPasswordView
# ---------------------------------------------------------------------------

class ResetPasswordView(APIView):
    """POST: Reset password with token from email."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = str(serializer.validated_data["token"])
        user_id = cache.get(f"password_reset_{token}")

        if not user_id:
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        cache.delete(f"password_reset_{token}")

        return Response({"detail": "Password reset successfully."})


# ---------------------------------------------------------------------------
# 9. GoogleOAuthCallbackView
# ---------------------------------------------------------------------------

class GoogleOAuthCallbackView(APIView):
    """POST: Handle Google OAuth callback, create/link user, return JWT."""

    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response(
                {"detail": "access_token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Requires SocialApp configuration in DB with Google credentials.
        # Frontend handles the OAuth redirect and passes the access_token.
        return Response(
            {"detail": "Google OAuth integration pending configuration."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


# ---------------------------------------------------------------------------
# 10. GitHubOAuthCallbackView
# ---------------------------------------------------------------------------

class GitHubOAuthCallbackView(APIView):
    """POST: Handle GitHub OAuth callback, create/link user, return JWT."""

    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response(
                {"detail": "code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Requires SocialApp configuration in DB with GitHub credentials.
        # Frontend handles the OAuth redirect and passes the code.
        return Response(
            {"detail": "GitHub OAuth integration pending configuration."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


# ---------------------------------------------------------------------------
# 11. UserOrganizationsView
# ---------------------------------------------------------------------------

class UserOrganizationsView(generics.ListAPIView):
    """GET: List all organizations the current user belongs to."""

    serializer_class = OrganizationMembershipSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrganizationMembership.objects.filter(
            user=self.request.user, is_active=True
        ).select_related("organization")


# ---------------------------------------------------------------------------
# 12. InviteAcceptView
# ---------------------------------------------------------------------------

class InviteAcceptView(APIView):
    """POST: Accept an organization invitation."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InviteAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "detail": "Invitation accepted successfully.",
            },
            status=status.HTTP_200_OK,
        )
