"""Root URL configuration for BuilderStream."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from apps.accounts.urls import auth_urlpatterns, user_urlpatterns
from apps.integrations.urls import public_api_urlpatterns
from apps.billing.urls import webhook_urlpatterns as stripe_webhook_urls
from apps.clients.urls import portal_urlpatterns
from apps.projects.urls import (
    action_item_urlpatterns,
    activity_urlpatterns,
    dashboard_urlpatterns,
)

urlpatterns = [
    # Root redirect to API docs
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/docs/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Authentication & User management
    path("api/v1/auth/", include((auth_urlpatterns, "auth"))),
    path("api/v1/users/", include((user_urlpatterns, "users"))),
    path("api/v1/auth/allauth/", include("allauth.urls")),
    # API v1 endpoints
    path("api/v1/core/", include("apps.core.urls", namespace="core")),
    path("api/v1/tenants/", include("apps.tenants.urls", namespace="tenants")),
    path("api/v1/billing/", include("apps.billing.urls", namespace="billing")),
    # Stripe webhook (separate from billing — no auth, no CSRF)
    path("api/v1/webhooks/stripe/", include((stripe_webhook_urls, "stripe_webhooks"))),
    path("api/v1/projects/", include("apps.projects.urls", namespace="projects")),
    path("api/v1/dashboard/", include((dashboard_urlpatterns, "dashboard"))),
    path("api/v1/action-items/", include((action_item_urlpatterns, "action_items"))),
    path("api/v1/activity/", include((activity_urlpatterns, "activity"))),
    path("api/v1/crm/", include("apps.crm.urls", namespace="crm")),
    path("api/v1/estimating/", include("apps.estimating.urls", namespace="estimating")),
    path("api/v1/scheduling/", include("apps.scheduling.urls", namespace="scheduling")),
    path("api/v1/financials/", include("apps.financials.urls", namespace="financials")),
    path("api/v1/clients/", include("apps.clients.urls", namespace="clients")),
    path("api/v1/portal/", include((portal_urlpatterns, "portal"))),
    path("api/v1/documents/", include("apps.documents.urls", namespace="documents")),
    path("api/v1/field-ops/", include("apps.field_ops.urls", namespace="field_ops")),
    path("api/v1/quality-safety/", include("apps.quality_safety.urls", namespace="quality_safety")),
    path("api/v1/payroll/", include("apps.payroll.urls", namespace="payroll")),
    path("api/v1/service/", include("apps.service.urls", namespace="service")),
    path("api/v1/analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("api/v1/integrations/", include("apps.integrations.urls", namespace="integrations")),
    path("api/v1/public/", include((public_api_urlpatterns, "public_api"))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
