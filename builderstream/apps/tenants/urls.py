"""Tenant URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "tenants"

router = DefaultRouter()
router.register("organizations", views.OrganizationViewSet)
router.register("memberships", views.MembershipViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
