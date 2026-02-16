"""Project URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "projects"

router = DefaultRouter()
router.register("", views.ProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
]

# Exported patterns for config/urls.py (separate top-level prefixes)
dashboard_urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("layout/", views.DashboardLayoutView.as_view(), name="dashboard-layout"),
]

action_item_router = DefaultRouter()
action_item_router.register("", views.ActionItemViewSet, basename="action-item")

action_item_urlpatterns = [
    path("", include(action_item_router.urls)),
]

activity_urlpatterns = [
    path("", views.ActivityStreamView.as_view(), name="activity-stream"),
]
