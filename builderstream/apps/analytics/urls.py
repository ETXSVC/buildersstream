"""Analytics URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "analytics"

router = DefaultRouter()
router.register("dashboards", views.DashboardViewSet)
router.register("reports", views.ReportViewSet)
router.register("kpis", views.KPIViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
