"""Quality & Safety URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "quality_safety"

router = DefaultRouter()
router.register("checklists", views.InspectionChecklistViewSet, basename="checklist")
router.register("inspections", views.InspectionViewSet, basename="inspection")
router.register("deficiencies", views.DeficiencyViewSet, basename="deficiency")
router.register("incidents", views.SafetyIncidentViewSet, basename="incident")
router.register("toolbox-talks", views.ToolboxTalkViewSet, basename="toolbox-talk")

analytics_urlpatterns = [
    path("quality-scores/", views.QualityScoresView.as_view(), name="quality-scores"),
    path("incident-trends/", views.IncidentTrendsView.as_view(), name="incident-trends"),
    path("deficiency-stats/", views.DeficiencyStatsView.as_view(), name="deficiency-stats"),
    path("safety-summary/", views.SafetySummaryView.as_view(), name="safety-summary"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/", include(analytics_urlpatterns)),
]
