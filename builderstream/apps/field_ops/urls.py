"""Field operations URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "field_ops"

router = DefaultRouter()
router.register("daily-logs", views.DailyLogViewSet)
router.register("time-entries", views.TimeEntryViewSet)
router.register("expenses", views.ExpenseViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
