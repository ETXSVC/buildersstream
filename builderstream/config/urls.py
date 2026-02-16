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
    path("api/v1/projects/", include("apps.projects.urls", namespace="projects")),
    path("api/v1/crm/", include("apps.crm.urls", namespace="crm")),
    path("api/v1/estimating/", include("apps.estimating.urls", namespace="estimating")),
    path("api/v1/scheduling/", include("apps.scheduling.urls", namespace="scheduling")),
    path("api/v1/financials/", include("apps.financials.urls", namespace="financials")),
    path("api/v1/clients/", include("apps.clients.urls", namespace="clients")),
    path("api/v1/documents/", include("apps.documents.urls", namespace="documents")),
    path("api/v1/field-ops/", include("apps.field_ops.urls", namespace="field_ops")),
    path("api/v1/quality-safety/", include("apps.quality_safety.urls", namespace="quality_safety")),
    path("api/v1/payroll/", include("apps.payroll.urls", namespace="payroll")),
    path("api/v1/service/", include("apps.service.urls", namespace="service")),
    path("api/v1/analytics/", include("apps.analytics.urls", namespace="analytics")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
