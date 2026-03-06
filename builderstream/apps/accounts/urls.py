"""Account URL configuration.

Exports two url pattern lists:
- auth_urlpatterns: mounted at /api/v1/auth/ (login, register, verify, password)
- user_urlpatterns: mounted at /api/v1/users/ (profile, organizations)
"""
from django.urls import path
from . import views
from apps.core.views import UserSessionListView, UserSessionRevokeView

# Auth endpoints (/api/v1/auth/)
auth_urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("token/refresh/", views.TokenRefreshWithCookieView.as_view(), name="token-refresh"),
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
    path("me/profile/", views.MeProfileView.as_view(), name="user-me-profile"),
    path("me/organizations/", views.UserOrganizationsView.as_view(), name="user-organizations"),
    # 2FA
    path("me/2fa/setup/", views.TwoFactorSetupView.as_view(), name="2fa-setup"),
    path("me/2fa/enable/", views.TwoFactorEnableView.as_view(), name="2fa-enable"),
    path("me/2fa/disable/", views.TwoFactorDisableView.as_view(), name="2fa-disable"),
    path("me/2fa/backup-codes/", views.TwoFactorBackupCodesView.as_view(), name="2fa-backup-codes"),
    # Session management
    path("me/sessions/", UserSessionListView.as_view(), name="session-list"),
    path("me/sessions/<uuid:pk>/", UserSessionRevokeView.as_view(), name="session-revoke"),
]
