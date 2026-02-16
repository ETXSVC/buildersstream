"""Tenant URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "tenants"

router = DefaultRouter()
router.register("organizations", views.OrganizationViewSet)
router.register("memberships", views.MembershipViewSet)
router.register("modules", views.ModuleViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("switch-organization/", views.SwitchOrganizationView.as_view(), name="switch-organization"),
]
