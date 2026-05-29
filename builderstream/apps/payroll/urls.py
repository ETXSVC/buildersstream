"""Payroll & Workforce Management URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CertifiedPayrollViewSet,
    ComplianceDashboardView,
    EmployeeViewSet,
    PayrollRunViewSet,
    PrevailingWageRateViewSet,
)

app_name = "payroll"

router = DefaultRouter()
router.register("employees", EmployeeViewSet)
router.register("payroll-runs", PayrollRunViewSet)
router.register("certified-reports", CertifiedPayrollViewSet)
router.register("prevailing-wage-rates", PrevailingWageRateViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("compliance/", ComplianceDashboardView.as_view(), name="compliance-dashboard"),
]
