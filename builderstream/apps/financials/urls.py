"""Financial Management Suite URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "financials"

router = DefaultRouter()
router.register("cost-codes", views.CostCodeViewSet)
router.register("budgets", views.BudgetViewSet)
router.register("expenses", views.ExpenseViewSet)
router.register("invoices", views.InvoiceViewSet)
router.register("invoice-line-items", views.InvoiceLineItemViewSet)
router.register("payments", views.PaymentViewSet)
router.register("change-orders", views.ChangeOrderViewSet)
router.register("change-order-line-items", views.ChangeOrderLineItemViewSet)
router.register("purchase-orders", views.PurchaseOrderViewSet)
router.register("purchase-order-line-items", views.PurchaseOrderLineItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Report views
    path("reports/job-cost/", views.JobCostReportView.as_view(), name="report-job-cost"),
    path("reports/cash-flow/", views.CashFlowForecastView.as_view(), name="report-cash-flow"),
]
