"""
Client Collaboration Portal URL configuration.

Two route groups:
  /api/v1/clients/   — Contractor-facing management endpoints (standard JWT auth)
  /api/v1/portal/    — Client-facing portal endpoints (Portal JWT auth)

Both groups are included from config/urls.py.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.clients import views

app_name = "clients"

# ---------------------------------------------------------------------------
# Contractor-facing router  →  /api/v1/clients/
# ---------------------------------------------------------------------------

contractor_router = DefaultRouter()
contractor_router.register("portal-access", views.ClientPortalAccessViewSet, basename="clientportalaccess")
contractor_router.register("selections", views.SelectionViewSet, basename="selection")
contractor_router.register("selection-options", views.SelectionOptionViewSet, basename="selectionoption")
contractor_router.register("approvals", views.ClientApprovalViewSet, basename="clientapproval")
contractor_router.register("messages", views.ClientMessageViewSet, basename="clientmessage")
contractor_router.register("branding", views.PortalBrandingViewSet, basename="portalbranding")
contractor_router.register("surveys", views.ClientSatisfactionSurveyViewSet, basename="clientsurvey")

contractor_urlpatterns = [
    path("", include(contractor_router.urls)),
]

# ---------------------------------------------------------------------------
# Client-facing portal routes  →  /api/v1/portal/
# ---------------------------------------------------------------------------

portal_urlpatterns = [
    path("login/", views.ClientLoginView.as_view(), name="portal-login"),
    path("dashboard/", views.ClientDashboardView.as_view(), name="portal-dashboard"),
    path("selections/", views.ClientSelectionsView.as_view(), name="portal-selections"),
    path("selections/<uuid:pk>/", views.ClientSelectionsView.as_view(), name="portal-selection-detail"),
    path("selections/<uuid:pk>/choose/", views.ClientSelectionsView.as_view(), name="portal-selection-choose"),
    path("approvals/", views.ClientApprovalsView.as_view(), name="portal-approvals"),
    path("approvals/<uuid:pk>/", views.ClientApprovalsView.as_view(), name="portal-approval-detail"),
    path("approvals/<uuid:pk>/respond/", views.ClientApprovalsView.as_view(), name="portal-approval-respond"),
    path("messages/", views.ClientMessagesView.as_view(), name="portal-messages"),
    path("schedule/", views.ClientScheduleView.as_view(), name="portal-schedule"),
    path("survey/", views.ClientSurveyView.as_view(), name="portal-survey"),
]

# Default urlpatterns (used when included without prefix — will be overridden in config/urls.py)
urlpatterns = contractor_urlpatterns
