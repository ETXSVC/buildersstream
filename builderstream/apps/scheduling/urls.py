"""Scheduling URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "scheduling"

router = DefaultRouter()
router.register("crews", views.CrewViewSet)
router.register("tasks", views.TaskViewSet)
router.register("dependencies", views.TaskDependencyViewSet, basename="taskdependency")
router.register("equipment", views.EquipmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
