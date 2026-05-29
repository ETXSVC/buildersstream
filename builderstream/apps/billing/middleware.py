"""Subscription enforcement middleware.

Ensures that organizations have an active (or trialing) subscription
before allowing API access.  Past-due orgs get read-only access.
Canceled/expired orgs get a 402 Payment Required response.
"""
from django.http import JsonResponse


class SubscriptionRequiredMiddleware:
    """Enforce subscription status on API requests.

    Must run AFTER TenantMiddleware (needs ``request.organization``).

    Access rules:
    - ACTIVE / TRIALING → full access
    - PAST_DUE → GET only (read-only), write methods return 402
    - CANCELED / other → 402 with upgrade prompt
    """

    # Paths that bypass subscription checks entirely
    EXEMPT_PREFIXES = (
        "/admin/",
        "/api/v1/auth/",
        "/api/v1/users/",
        "/api/v1/billing/",
        "/api/v1/webhooks/",
        "/api/v1/tenants/organizations/",
        "/api/docs/",
    )

    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check authenticated API requests with an org context
        org = getattr(request, "organization", None)
        if org is None or not request.path.startswith("/api/"):
            return self.get_response(request)

        # Skip exempt paths
        if any(request.path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        status = org.subscription_status

        # Active or trialing — full access
        if status in ("active", "trialing"):
            return self.get_response(request)

        # Past due — read-only access
        if status == "past_due":
            if request.method in self.WRITE_METHODS:
                return JsonResponse(
                    {
                        "detail": "Your subscription payment is past due. "
                        "Please update your payment method to restore full access.",
                        "code": "subscription_past_due",
                    },
                    status=402,
                )
            return self.get_response(request)

        # Canceled or any other status — blocked
        return JsonResponse(
            {
                "detail": "Your subscription is inactive. "
                "Please subscribe to a plan to continue using BuilderStream.",
                "code": "subscription_required",
            },
            status=402,
        )
