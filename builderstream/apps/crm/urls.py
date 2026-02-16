"""CRM URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "crm"

router = DefaultRouter()
router.register("contacts", views.ContactViewSet)
router.register("stages", views.PipelineStageViewSet)
router.register("deals", views.DealViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
