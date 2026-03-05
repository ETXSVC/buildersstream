"""Core views."""
from django.db import models
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return Response({"status": "ok"})


class AuditLogView(APIView):
    """GET /api/v1/core/audit-log/ — paginated audit log for org admins."""

    def get(self, request):
        from apps.core.models import AuditLog

        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        org = getattr(request, "organization", None)
        if not org:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        qs = AuditLog.objects.filter(org=org).select_related("user").order_by("-created_at")

        action = request.query_params.get("action")
        user_id = request.query_params.get("user_id")
        ip = request.query_params.get("ip_address")
        if action:
            qs = qs.filter(action=action)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if ip:
            qs = qs.filter(ip_address=ip)

        page_size = 50
        try:
            page = max(1, int(request.query_params.get("page", 1)))
        except (ValueError, TypeError):
            page = 1
        offset = (page - 1) * page_size
        total = qs.count()
        logs = qs[offset: offset + page_size]

        data = [
            {
                "id": str(log.id),
                "action": log.action,
                "user_email": log.user.email if log.user else None,
                "ip_address": log.ip_address,
                "path": log.path,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
        return Response({"count": total, "page": page, "results": data})


class UserSessionListView(APIView):
    """GET /api/v1/users/me/sessions/ — list user's active sessions."""

    def get(self, request):
        from apps.core.models import UserSession
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        data = [
            {
                "id": str(s.id),
                "device_name": s.device_name,
                "ip_address": s.ip_address,
                "last_active": s.last_active.isoformat(),
                "created_at": s.created_at.isoformat(),
            }
            for s in sessions
        ]
        return Response(data)


class UserSessionRevokeView(APIView):
    """DELETE /api/v1/users/me/sessions/{pk}/ — revoke a session."""

    def delete(self, request, pk):
        from apps.core.models import UserSession
        try:
            session = UserSession.objects.get(pk=pk, user=request.user, is_active=True)
        except UserSession.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        session.is_active = False
        session.revoked_at = timezone.now()
        session.save(update_fields=["is_active", "revoked_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class UniversalSearchView(APIView):
    """GET /api/v1/core/search/?q=<query>

    Returns up to 5 results per entity type:
    Projects, Contacts, Leads, Estimates, Documents, Invoices.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if len(q) < 2:
            return Response({"results": []})

        org = getattr(request, "organization", None)
        if not org:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        results = []
        results += self._search_projects(q, org)
        results += self._search_contacts(q, org)
        results += self._search_leads(q, org)
        results += self._search_estimates(q, org)
        results += self._search_invoices(q, org)
        results += self._search_documents(q, org)

        return Response({"results": results, "query": q})

    @staticmethod
    def _search_projects(q, org):
        try:
            from apps.projects.models import Project
            qs = Project.objects.filter(
                organization=org
            ).filter(
                models.Q(name__icontains=q) | models.Q(project_number__icontains=q)
            )[:5]
            return [
                {"type": "project", "id": str(p.id), "title": p.name,
                 "subtitle": p.project_number, "url": f"/projects/{p.id}"}
                for p in qs
            ]
        except Exception:
            return []

    @staticmethod
    def _search_contacts(q, org):
        try:
            from apps.crm.models import Contact
            qs = Contact.objects.filter(
                organization=org
            ).filter(
                models.Q(first_name__icontains=q) | models.Q(last_name__icontains=q) | models.Q(email__icontains=q)
            )[:5]
            return [
                {"type": "contact", "id": str(c.id),
                 "title": f"{c.first_name} {c.last_name}".strip() or c.email,
                 "subtitle": c.email, "url": "/crm"}
                for c in qs
            ]
        except Exception:
            return []

    @staticmethod
    def _search_leads(q, org):
        try:
            from apps.crm.models import Lead
            qs = Lead.objects.filter(
                organization=org
            ).filter(
                models.Q(title__icontains=q)
            )[:5]
            return [
                {"type": "lead", "id": str(l.id), "title": l.title,
                 "subtitle": l.get_status_display(), "url": "/crm"}
                for l in qs
            ]
        except Exception:
            return []

    @staticmethod
    def _search_estimates(q, org):
        try:
            from apps.estimating.models import Estimate
            qs = Estimate.objects.filter(
                organization=org
            ).filter(
                models.Q(name__icontains=q) | models.Q(estimate_number__icontains=q)
            )[:5]
            return [
                {"type": "estimate", "id": str(e.id), "title": e.name,
                 "subtitle": e.estimate_number, "url": "/estimating"}
                for e in qs
            ]
        except Exception:
            return []

    @staticmethod
    def _search_invoices(q, org):
        try:
            from apps.financials.models import Invoice
            qs = Invoice.objects.filter(
                organization=org
            ).filter(
                models.Q(invoice_number__icontains=q)
            )[:5]
            return [
                {"type": "invoice", "id": str(i.id), "title": f"Invoice {i.invoice_number}",
                 "subtitle": i.get_status_display(), "url": "/financials"}
                for i in qs
            ]
        except Exception:
            return []

    @staticmethod
    def _search_documents(q, org):
        try:
            from apps.documents.models import Document
            qs = Document.objects.filter(
                organization=org
            ).filter(
                models.Q(name__icontains=q)
            )[:5]
            return [
                {"type": "document", "id": str(d.id), "title": d.name,
                 "subtitle": d.file_type or "document", "url": "/documents"}
                for d in qs
            ]
        except Exception:
            return []
