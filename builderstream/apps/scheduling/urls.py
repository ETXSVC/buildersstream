"""Scheduling URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "scheduling"

router = DefaultRouter()
router.register("crews", views.CrewViewSet)
router.register("tasks", views.ScheduleTaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
