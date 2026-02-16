"""Estimating URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "estimating"

router = DefaultRouter()
router.register("cost-codes", views.CostCodeViewSet)
router.register("estimates", views.EstimateViewSet)
router.register("line-items", views.EstimateLineItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
