"""
Security middleware for BuilderStream.

AuditLogMiddleware — logs authentication events to AuditLog.
IPWhitelistMiddleware — enforces per-org IP allowlists for sensitive paths.
"""
import ipaddress
import logging

logger = logging.getLogger(__name__)

# Paths that trigger audit logging on every response
_AUDIT_PATHS = {
    "/api/v1/auth/login/",
    "/api/v1/auth/logout/",
    "/api/v1/users/me/2fa/enable/",
    "/api/v1/users/me/2fa/disable/",
    "/api/v1/auth/change-password/",
    "/api/v1/tenants/invitations/",
}

# Status codes that indicate a permission failure
_PERMISSION_DENIED_STATUSES = {401, 403}


def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class AuditLogMiddleware:
    """Write security-relevant events to AuditLog after each response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._maybe_log(request, response)
        except Exception:
            logger.exception("AuditLogMiddleware failed to log")
        return response

    def _maybe_log(self, request, response):
        from apps.core.models import AuditLog

        path = request.path
        method = request.method
        status = response.status_code
        user = getattr(request, "user", None)
        if user and not user.is_authenticated:
            user = None
        org = getattr(request, "organization", None)
        ip = _get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")

        # Log specific auth paths
        if path in _AUDIT_PATHS and method == "POST":
            action_map = {
                "/api/v1/auth/login/": (
                    AuditLog.Action.LOGIN if status < 400 else AuditLog.Action.LOGIN_FAILED
                ),
                "/api/v1/auth/logout/": AuditLog.Action.LOGOUT,
                "/api/v1/users/me/2fa/enable/": AuditLog.Action.TWO_FACTOR_ENABLED,
                "/api/v1/users/me/2fa/disable/": AuditLog.Action.TWO_FACTOR_DISABLED,
                "/api/v1/auth/change-password/": AuditLog.Action.PASSWORD_CHANGED,
            }
            action = action_map.get(path)
            if action and (status < 400 or path == "/api/v1/auth/login/"):
                AuditLog.log(
                    action=action,
                    user=user,
                    org=org,
                    ip_address=ip or None,
                    user_agent=ua,
                    path=path,
                    details={"status_code": status},
                )

        # Log all 401/403 responses for security monitoring
        elif status in _PERMISSION_DENIED_STATUSES:
            AuditLog.log(
                action=AuditLog.Action.PERMISSION_DENIED,
                user=user,
                org=org,
                ip_address=ip or None,
                user_agent=ua,
                path=path,
                details={"status_code": status, "method": method},
            )


class IPWhitelistMiddleware:
    """
    If an organization has IP whitelisting enabled, reject requests from
    non-whitelisted IPs for admin-level operations.

    Only activates when the org has at least one active IPWhitelist entry.
    Skipped for public/webhook/portal endpoints.
    """

    EXEMPT_PREFIXES = (
        "/api/v1/webhooks/",
        "/api/v1/portal/",
        "/api/v1/public/",
        "/api/docs/",
        "/admin/",
        "/static/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._is_exempt(request.path):
            org = getattr(request, "organization", None)
            if org and not self._ip_allowed(request, org):
                from django.http import JsonResponse
                return JsonResponse(
                    {"detail": "Access denied: IP not whitelisted."},
                    status=403,
                )
        return self.get_response(request)

    def _is_exempt(self, path):
        return any(path.startswith(p) for p in self.EXEMPT_PREFIXES)

    def _ip_allowed(self, request, org):
        from apps.core.models import IPWhitelist

        entries = IPWhitelist.objects.filter(org=org, is_active=True)
        if not entries.exists():
            return True  # No whitelist configured → allow all

        client_ip = _get_client_ip(request)
        if not client_ip:
            return True

        try:
            client_addr = ipaddress.ip_address(client_ip)
        except ValueError:
            return False

        for entry in entries:
            try:
                network = ipaddress.ip_network(entry.cidr, strict=False)
                if client_addr in network:
                    return True
            except ValueError:
                continue
        return False
