"""Financial URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "financials"

router = DefaultRouter()
router.register("budgets", views.BudgetViewSet)
router.register("invoices", views.InvoiceViewSet)
router.register("change-orders", views.ChangeOrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
