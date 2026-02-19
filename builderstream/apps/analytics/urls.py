"""Analytics & Reporting Engine URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AnalyticsSummaryView,
    DashboardViewSet,
    KPIViewSet,
    ReportViewSet,
)

app_name = "analytics"

router = DefaultRouter()
router.register("dashboards", DashboardViewSet)
router.register("reports", ReportViewSet)
router.register("kpis", KPIViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("summary/", AnalyticsSummaryView.as_view(), name="summary"),
]
