"""Field operations URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "field_ops"

router = DefaultRouter()
router.register("daily-logs", views.DailyLogViewSet)
router.register("time-entries", views.TimeEntryViewSet)
router.register("expenses", views.ExpenseEntryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Aggregate views
    path("timesheets/summary/", views.TimesheetSummaryView.as_view(), name="timesheet-summary"),
    path("daily-logs/calendar/", views.DailyLogCalendarView.as_view(), name="daily-log-calendar"),
]
