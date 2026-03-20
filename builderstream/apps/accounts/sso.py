"""SAML 2.0 SSO — views, helpers, and SSOConfiguration model.

Enterprise orgs can configure an Identity Provider (Okta, Azure AD, Google
Workspace SAML, etc.) to enable single sign-on for their users.

Flow:
  1. Admin configures IdP metadata in Settings → Security → SSO.
  2. User on /login enters their email → POST /api/v1/auth/sso/init/?email=...
     → API returns the IdP redirect URL.
  3. User is redirected to IdP.
  4. IdP POSTs a SAML assertion to the ACS endpoint:
         POST /api/v1/auth/sso/acs/
  5. ACS validates the assertion, looks up or creates the user, issues JWT.
  6. Redirect to /sso-callback?access=...&refresh=... in the SPA.
"""
import logging

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.core.models import TenantModel

logger = logging.getLogger(__name__)
User = get_user_model()


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class SSOConfiguration(TenantModel):
    """SAML 2.0 Identity Provider configuration for an organization."""

    # IdP-provided metadata
    idp_entity_id = models.CharField(max_length=500, blank=True, help_text="IdP EntityID (issuer)")
    idp_sso_url = models.URLField(max_length=500, blank=True, help_text="IdP Single Sign-On URL")
    idp_slo_url = models.URLField(max_length=500, blank=True, help_text="IdP Single Logout URL")
    idp_x509_cert = models.TextField(blank=True, help_text="IdP X.509 certificate (PEM, no headers)")

    # SP settings
    is_enabled = models.BooleanField(default=False)
    auto_provision = models.BooleanField(
        default=True,
        help_text="Automatically create user accounts on first SSO login",
    )
    default_role = models.CharField(
        max_length=20, default="read_only",
        help_text="Role assigned to auto-provisioned users",
    )

    # Attribute mapping (IdP attribute name → User field)
    attr_email = models.CharField(max_length=200, default="email")
    attr_first_name = models.CharField(max_length=200, default="firstName")
    attr_last_name = models.CharField(max_length=200, default="lastName")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SSO Config for {self.organization} ({'enabled' if self.is_enabled else 'disabled'})"

    def to_saml_settings(self, request) -> dict:
        """Build the settings dict expected by python3-saml."""
        sp_base = request.build_absolute_uri("/")
        acs_url = request.build_absolute_uri("/api/v1/auth/sso/acs/")
        return {
            "strict": True,
            "debug": False,
            "sp": {
                "entityId": f"{sp_base}saml/metadata/{self.organization_id}/",
                "assertionConsumerService": {
                    "url": acs_url,
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                },
                "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
            },
            "idp": {
                "entityId": self.idp_entity_id,
                "singleSignOnService": {
                    "url": self.idp_sso_url,
                    "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                },
                "x509cert": self.idp_x509_cert,
            },
            "security": {
                "wantAssertionsSigned": True,
                "wantResponseSigned": True,
            },
        }


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class SSOInitView(APIView):
    """Return the IdP redirect URL for a user's email domain."""

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        if not email:
            return Response({"detail": "email required."}, status=400)

        domain = email.split("@")[-1]
        # Find an enabled SSO config whose org has a member with this email domain
        config = _find_sso_config_for_domain(domain)
        if not config:
            return Response({"sso_available": False})

        try:
            from onelogin.saml2.auth import OneLogin_Saml2_Auth
            req = _prepare_saml_request(request)
            auth = OneLogin_Saml2_Auth(req, config.to_saml_settings(request))
            redirect_url = auth.login(return_to=f"/sso-callback?org={config.organization_id}")
            return Response({"sso_available": True, "redirect_url": redirect_url})
        except Exception as exc:
            logger.error("SSO init failed: %s", exc)
            return Response({"detail": "SSO configuration error."}, status=503)


class SSOACSView(APIView):
    """Assertion Consumer Service — receives SAML response from IdP."""

    permission_classes = [AllowAny]

    def post(self, request):
        org_id = request.data.get("RelayState", "").replace("/sso-callback?org=", "")
        if not org_id:
            return Response({"detail": "Missing RelayState."}, status=400)

        try:
            config = SSOConfiguration.objects.select_related("organization").get(
                organization_id=org_id, is_enabled=True
            )
        except SSOConfiguration.DoesNotExist:
            return Response({"detail": "SSO not configured for this organization."}, status=400)

        try:
            from onelogin.saml2.auth import OneLogin_Saml2_Auth
            req = _prepare_saml_request(request)
            auth = OneLogin_Saml2_Auth(req, config.to_saml_settings(request))
            auth.process_response()
            errors = auth.get_errors()
            if errors:
                return Response({"detail": f"SAML errors: {errors}"}, status=400)
        except Exception as exc:
            logger.error("SAML ACS processing failed: %s", exc)
            return Response({"detail": "SAML processing error."}, status=400)

        # Extract user attributes
        attrs = auth.get_attributes()
        email = (attrs.get(config.attr_email, [None])[0] or "").lower().strip()
        first_name = attrs.get(config.attr_first_name, [""])[0]
        last_name = attrs.get(config.attr_last_name, [""])[0]

        if not email:
            return Response({"detail": "IdP did not provide an email attribute."}, status=400)

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "email_verified": True,
                "is_active": True,
            },
        )

        if created and config.auto_provision:
            # Add user to the organization with the default role
            from apps.tenants.models import OrganizationMembership
            OrganizationMembership.objects.get_or_create(
                user=user,
                organization=config.organization,
                defaults={"role": config.default_role, "is_active": True},
            )
            logger.info("SSO auto-provisioned user %s for org %s", email, config.organization_id)

        # Issue JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        # Deliver tokens as HttpOnly cookies — never in the URL or JS-accessible storage.
        # The SPA at /sso-callback calls hydrate() which picks up the cookies automatically.
        from django.http import HttpResponseRedirect
        secure = request.is_secure()
        response = HttpResponseRedirect(
            request.build_absolute_uri(f"/sso-callback?org={config.organization_id}")
        )
        response.set_cookie(
            "bs_access", str(refresh.access_token),
            httponly=True, secure=secure, samesite="Lax",
            max_age=int(refresh.access_token.lifetime.total_seconds()),
        )
        response.set_cookie(
            "bs_refresh", str(refresh),
            httponly=True, secure=secure, samesite="Lax",
            max_age=int(refresh.lifetime.total_seconds()),
        )
        return response


class SSOMetadataView(APIView):
    """Return SP SAML metadata XML for a given org (for IdP configuration)."""

    permission_classes = [AllowAny]

    def get(self, request, org_id):
        try:
            config = SSOConfiguration.objects.get(organization_id=org_id, is_enabled=True)
        except SSOConfiguration.DoesNotExist:
            return Response({"detail": "SSO not configured."}, status=404)

        try:
            from onelogin.saml2.metadata import OneLogin_Saml2_Metadata
            settings_dict = config.to_saml_settings(request)
            metadata = OneLogin_Saml2_Metadata.builder(settings_dict["sp"])
            from django.http import HttpResponse
            return HttpResponse(metadata, content_type="application/xml")
        except Exception as exc:
            logger.error("SAML metadata generation failed: %s", exc)
            return Response({"detail": "Metadata generation error."}, status=500)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_sso_config_for_domain(domain: str):
    """Find an enabled SSOConfiguration whose org has members with the given email domain."""
    from apps.tenants.models import OrganizationMembership
    org_ids = OrganizationMembership.objects.filter(
        user__email__endswith=f"@{domain}", is_active=True
    ).values_list("organization_id", flat=True).distinct()

    return SSOConfiguration.objects.filter(
        organization_id__in=org_ids, is_enabled=True
    ).select_related("organization").first()


def _prepare_saml_request(request) -> dict:
    """Build the request dict expected by python3-saml from a DRF request."""
    return {
        "https": "on" if request.is_secure() else "off",
        "http_host": request.get_host(),
        "script_name": request.path,
        "server_port": request.get_port(),
        "get_data": dict(request.query_params),
        "post_data": dict(request.data),
        "query_string": request.META.get("QUERY_STRING", ""),
    }
