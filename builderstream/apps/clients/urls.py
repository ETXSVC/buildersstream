"""Client portal URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "clients"

router = DefaultRouter()
router.register("access", views.ClientPortalAccessViewSet)
router.register("selections", views.SelectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
