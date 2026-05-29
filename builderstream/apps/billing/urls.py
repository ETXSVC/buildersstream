"""Billing URL configuration."""
from django.urls import path

from . import views
from .webhooks import StripeWebhookView

app_name = "billing"

urlpatterns = [
    path("subscription/", views.SubscriptionView.as_view(), name="subscription"),
    path("portal/", views.BillingPortalView.as_view(), name="billing-portal"),
    path("invoices/", views.InvoiceListView.as_view(), name="invoice-list"),
    path("plans/", views.PlanComparisonView.as_view(), name="plan-comparison"),
]

# Webhook URL — mounted separately in config/urls.py at /api/v1/webhooks/stripe/
webhook_urlpatterns = [
    path("", StripeWebhookView.as_view(), name="stripe-webhook"),
]
