"""Payroll URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "payroll"

router = DefaultRouter()
router.register("pay-periods", views.PayPeriodViewSet)
router.register("records", views.PayrollRecordViewSet)
router.register("certified", views.CertifiedPayrollViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
