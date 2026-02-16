"""Account URL configuration.

Exports two url pattern lists:
- auth_urlpatterns: mounted at /api/v1/auth/ (login, register, verify, password)
- user_urlpatterns: mounted at /api/v1/users/ (profile, organizations)
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

# Auth endpoints (/api/v1/auth/)
auth_urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("resend-verification/", views.ResendVerificationView.as_view(), name="resend-verification"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("invite/accept/", views.InviteAcceptView.as_view(), name="invite-accept"),
    # OAuth
    path("oauth/google/", views.GoogleOAuthCallbackView.as_view(), name="oauth-google"),
    path("oauth/github/", views.GitHubOAuthCallbackView.as_view(), name="oauth-github"),
]

# User endpoints (/api/v1/users/)
user_urlpatterns = [
    path("me/", views.ProfileView.as_view(), name="user-profile"),
    path("me/organizations/", views.UserOrganizationsView.as_view(), name="user-organizations"),
]
