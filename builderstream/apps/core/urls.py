"""Core URL configuration."""
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("audit-log/", views.AuditLogView.as_view(), name="audit-log"),
    path("search/", views.UniversalSearchView.as_view(), name="search"),
]
