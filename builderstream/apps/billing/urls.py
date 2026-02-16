"""Billing URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "billing"

router = DefaultRouter()
router.register("plans", views.PlanViewSet)
router.register("subscriptions", views.SubscriptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
