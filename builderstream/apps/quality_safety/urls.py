"""Quality and safety URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "quality_safety"

router = DefaultRouter()
router.register("inspections", views.InspectionViewSet)
router.register("incidents", views.SafetyIncidentViewSet)
router.register("checklists", views.SafetyChecklistViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
