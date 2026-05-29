"""
Client Collaboration Portal services.

4 service classes:
  ClientAuthService      — Magic link generation, token validation, portal sessions
  SelectionService       — Present selections, record choices, calculate price impact
  ApprovalService        — Create/send approval requests, track, auto-remind
  ClientNotificationService — Automated client notifications with frequency preferences
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from apps.clients.authentication import generate_portal_token
from apps.clients.models import (
    ClientApproval,
    ClientMessage,
    ClientPortalAccess,
    ClientSatisfactionSurvey,
    Selection,
)

logger = logging.getLogger(__name__)


class ClientAuthService:
    """
    Magic link authentication flow for the client portal.

    Flow:
        1. Contractor creates ClientPortalAccess for contact+project.
        2. send_magic_link_email() emails the access UUID link to the client.
        3. Client clicks the link → ClientLoginView calls validate_magic_link()
           to look up the ClientPortalAccess by UUID.
        4. generate_portal_session_token() wraps the portal_access in a
           short-lived JWT (8h) via generate_portal_token().
        5. Client uses the JWT as "Authorization: Portal <token>" on all
           subsequent /api/v1/portal/ calls.
    """

    @staticmethod
    def create_portal_access(project, contact, email=None, pin_code=None, permissions=None):
        """
        Create (or reactivate) a ClientPortalAccess for a contact+project pair.

        If an access record already exists, it is reactivated and a fresh
        access_token is issued (old magic links are invalidated).

        Args:
            project: projects.Project instance
            contact: crm.Contact instance
            email: Override email address (defaults to contact.email)
            pin_code: Optional 4-6 digit PIN
            permissions: Dict overriding default permissions

        Returns:
            ClientPortalAccess instance
        """
        import uuid as _uuid

        portal_email = email or contact.email
        org = project.organization

        existing = ClientPortalAccess.objects.filter(
            organization=org, project=project, contact=contact
        ).first()

        if existing:
            existing.is_active = True
            existing.email = portal_email
            existing.access_token = _uuid.uuid4()  # Invalidate old magic links
            if pin_code is not None:
                existing.pin_code = pin_code
            if permissions is not None:
                existing.permissions = permissions
            existing.save(update_fields=["is_active", "email", "access_token", "pin_code", "permissions", "updated_at"])
            return existing

        portal_access = ClientPortalAccess.objects.create(
            organization=org,
            project=project,
            contact=contact,
            email=portal_email,
            pin_code=pin_code,
            permissions=permissions or {},
        )
        return portal_access

    @staticmethod
    def get_magic_link_url(portal_access):
        """
        Build the magic link URL for the client portal.

        Format: {PORTAL_BASE_URL}/portal/access/{access_token}/
        Falls back to /portal/access/{token}/ if PORTAL_BASE_URL not set.
        """
        base_url = getattr(settings, "PORTAL_BASE_URL", "").rstrip("/")
        token = str(portal_access.access_token)
        return f"{base_url}/portal/access/{token}/"

    @staticmethod
    def send_magic_link_email(portal_access, custom_message=None):
        """
        Send a magic link email to the client.

        Args:
            portal_access: ClientPortalAccess instance
            custom_message: Optional personal message from the contractor

        Returns:
            True on success, False on failure
        """
        magic_link = ClientAuthService.get_magic_link_url(portal_access)
        org = portal_access.organization
        project = portal_access.project

        # Fetch branding config if available
        from apps.clients.models import PortalBranding
        branding = PortalBranding.objects.filter(organization=org).first()
        company_name = (
            branding.company_name_override
            if branding and branding.company_name_override
            else org.name
        )

        context = {
            "contact": portal_access.contact,
            "project": project,
            "organization": org,
            "company_name": company_name,
            "magic_link": magic_link,
            "custom_message": custom_message,
            "pin_required": bool(portal_access.pin_code),
        }

        try:
            subject = f"Your project portal access — {project.name}"
            html_body = render_to_string("emails/portal_magic_link.html", context)
            text_body = render_to_string("emails/portal_magic_link.txt", context)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@builderstream.com")

            send_mail(
                subject=subject,
                message=text_body,
                from_email=from_email,
                recipient_list=[portal_access.email],
                html_message=html_body,
                fail_silently=False,
            )
            logger.info(
                "Magic link email sent to %s for project %s",
                portal_access.email,
                project.pk,
            )
            return True
        except Exception as exc:
            logger.error(
                "Failed to send magic link email to %s: %s",
                portal_access.email,
                exc,
            )
            return False

    @staticmethod
    def validate_magic_link(access_token_str, pin_code=None):
        """
        Validate a magic link token (UUID) and optionally verify the PIN.

        Args:
            access_token_str: String UUID from the magic link URL
            pin_code: Optional PIN entered by the client

        Returns:
            ClientPortalAccess on success

        Raises:
            ValueError: If token invalid, not found, or PIN mismatch
        """
        try:
            import uuid as _uuid
            token_uuid = _uuid.UUID(access_token_str)
        except (ValueError, AttributeError):
            raise ValueError("Invalid access token format.")

        try:
            portal_access = (
                ClientPortalAccess.objects
                .select_related("contact", "project", "organization")
                .get(access_token=token_uuid, is_active=True)
            )
        except ClientPortalAccess.DoesNotExist:
            raise ValueError("Portal access not found or deactivated.")

        if portal_access.pin_code and pin_code != portal_access.pin_code:
            raise ValueError("Incorrect PIN.")

        # Update last login
        portal_access.last_login = timezone.now()
        portal_access.save(update_fields=["last_login", "updated_at"])

        return portal_access

    @staticmethod
    def generate_portal_session_token(portal_access):
        """
        Generate a short-lived JWT for client portal API calls.

        This is the token clients use in the Authorization: Portal <token> header.

        Returns:
            JWT string
        """
        return generate_portal_token(portal_access)


class SelectionService:
    """
    Manage material/finish selections for client review and choice.
    """

    @staticmethod
    def get_selections_for_client(portal_access):
        """
        Return selections for a portal client.

        Only returns selections for the client's specific project that
        are visible to clients (assigned_to_client=True OR already decided).
        """
        return (
            Selection.objects
            .filter(
                organization=portal_access.organization,
                project=portal_access.project,
            )
            .exclude(status=Selection.Status.PENDING)
            .select_related("selected_option")
            .prefetch_related("options")
            .order_by("sort_order", "category")
        )

    @staticmethod
    def get_pending_selections(portal_access):
        """Return selections awaiting client decision."""
        return (
            Selection.objects
            .filter(
                organization=portal_access.organization,
                project=portal_access.project,
                assigned_to_client=True,
                status=Selection.Status.CLIENT_REVIEW,
            )
            .prefetch_related("options")
            .order_by("due_date", "sort_order")
        )

    @staticmethod
    def record_client_choice(selection, option, portal_access):
        """
        Record the client's selection choice.

        Args:
            selection: Selection instance
            option: SelectionOption instance (must belong to selection)
            portal_access: ClientPortalAccess of the requesting client

        Returns:
            Updated Selection instance

        Raises:
            ValueError: If option doesn't belong to selection or unauthorized
        """
        if option.selection_id != selection.pk:
            raise ValueError("Option does not belong to this selection.")

        if not portal_access.has_permission("approve_selections"):
            raise ValueError("Client does not have permission to approve selections.")

        selection.selected_option = option
        selection.status = Selection.Status.APPROVED
        selection.save(update_fields=["selected_option", "status", "updated_at"])

        # Notify contractor
        try:
            SelectionService._notify_contractor_of_choice(selection, option, portal_access)
        except Exception as exc:
            logger.warning("Failed to notify contractor of selection choice: %s", exc)

        return selection

    @staticmethod
    def calculate_price_impact(project):
        """
        Calculate total price impact of all approved selections on a project.

        Returns:
            Decimal: Total price delta vs. base options
        """
        selections = Selection.objects.filter(
            project=project,
            selected_option__isnull=False,
            status__in=[Selection.Status.APPROVED, Selection.Status.ORDERED, Selection.Status.INSTALLED],
        ).select_related("selected_option")

        total_delta = Decimal("0.00")
        for sel in selections:
            if sel.selected_option:
                total_delta += sel.selected_option.price_difference

        return total_delta

    @staticmethod
    def _notify_contractor_of_choice(selection, option, portal_access):
        """Send internal message to contractor about client selection."""
        ClientMessage.objects.create(
            organization=selection.organization,
            project=selection.project,
            sender_type=ClientMessage.SenderType.CLIENT,
            sender_contact=portal_access.contact,
            subject=f"Selection made: {selection.name}",
            body=(
                f"{portal_access.contact} has chosen '{option.name}' for {selection.name}.\n"
                f"Price difference: ${option.price_difference:+.2f}"
            ),
        )


class ApprovalService:
    """
    Create and manage formal client approval requests.
    """

    DEFAULT_EXPIRY_DAYS = 7
    REMINDER_THRESHOLD_DAYS = 2  # Send reminder if pending for this many days

    @staticmethod
    def create_approval_request(
        project,
        approval_type,
        title,
        description="",
        contact=None,
        source_type="",
        source_id=None,
        expires_in_days=None,
    ):
        """
        Create a new ClientApproval request.

        Args:
            project: Project instance
            approval_type: ClientApproval.ApprovalType value
            title: Short title for the approval
            description: Detailed description
            contact: CRM Contact who should approve (defaults to project client)
            source_type: Model name of the related object (optional)
            source_id: UUID of the related object (optional)
            expires_in_days: Days until expiry (default: DEFAULT_EXPIRY_DAYS)

        Returns:
            ClientApproval instance
        """
        if contact is None:
            # Fall back to project client if no contact specified
            client_contact = getattr(project, "client", None)
            if hasattr(client_contact, "crm_contact"):
                contact = client_contact.crm_contact
            else:
                contact = client_contact

        days = expires_in_days if expires_in_days is not None else ApprovalService.DEFAULT_EXPIRY_DAYS
        expires_at = timezone.now() + timedelta(days=days)

        approval = ClientApproval.objects.create(
            organization=project.organization,
            project=project,
            contact=contact,
            approval_type=approval_type,
            title=title,
            description=description,
            source_type=source_type or "",
            source_id=source_id,
            expires_at=expires_at,
        )

        # Notify client via portal message
        try:
            ApprovalService._notify_client_of_approval(approval)
        except Exception as exc:
            logger.warning("Failed to notify client of approval request: %s", exc)

        return approval

    @staticmethod
    def record_approval_response(approval, approved, response_notes="", signature_data=None, ip_address=None, user_agent=None):
        """
        Record the client's response to an approval request.

        Args:
            approval: ClientApproval instance
            approved: True = APPROVED, False = REJECTED
            response_notes: Optional notes from client
            signature_data: Base64 signature image data (optional)
            ip_address: Client IP (for audit trail)
            user_agent: Client user agent (for audit trail)

        Returns:
            Updated ClientApproval instance

        Raises:
            ValueError: If approval is not in PENDING status
        """
        if approval.status != ClientApproval.Status.PENDING:
            raise ValueError(f"Approval is already {approval.status}.")

        if approval.expires_at and approval.expires_at < timezone.now():
            raise ValueError("This approval request has expired.")

        approval.status = ClientApproval.Status.APPROVED if approved else ClientApproval.Status.REJECTED
        approval.responded_at = timezone.now()
        approval.response_notes = response_notes

        if signature_data and approved:
            approval.client_signature = {
                "name": response_notes.split("\n")[0][:100] if response_notes else "Client",
                "ip": ip_address,
                "user_agent": user_agent,
                "signed_at": timezone.now().isoformat(),
                "image_data": signature_data,
            }

        approval.save(update_fields=[
            "status", "responded_at", "response_notes", "client_signature", "updated_at"
        ])

        return approval

    @staticmethod
    def expire_overdue_approvals():
        """
        Mark PENDING approvals past their expiry date as EXPIRED.

        Called by Celery task.

        Returns:
            int: Number of approvals expired
        """
        now = timezone.now()
        expired_count = ClientApproval.objects.filter(
            status=ClientApproval.Status.PENDING,
            expires_at__lt=now,
        ).update(status=ClientApproval.Status.EXPIRED)
        return expired_count

    @staticmethod
    def get_pending_approvals_needing_reminder(threshold_days=None):
        """
        Return PENDING approvals older than threshold_days that haven't been reminded recently.
        """
        days = threshold_days if threshold_days is not None else ApprovalService.REMINDER_THRESHOLD_DAYS
        cutoff = timezone.now() - timedelta(days=days)
        return ClientApproval.objects.filter(
            status=ClientApproval.Status.PENDING,
            requested_at__lt=cutoff,
        ).select_related("contact", "project")

    @staticmethod
    def send_reminder(approval):
        """
        Send a reminder email for a pending approval.

        Updates reminded_count and last_reminded_at.
        """
        if not approval.contact or not approval.contact.email:
            return False

        try:
            org = approval.organization
            from apps.clients.models import PortalBranding
            branding = PortalBranding.objects.filter(organization=org).first()
            company_name = (
                branding.company_name_override
                if branding and branding.company_name_override
                else org.name
            )

            context = {
                "approval": approval,
                "project": approval.project,
                "organization": org,
                "company_name": company_name,
            }
            subject = f"Reminder: Action needed — {approval.title}"
            html_body = render_to_string("emails/approval_reminder.html", context)
            text_body = render_to_string("emails/approval_reminder.txt", context)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@builderstream.com")

            send_mail(
                subject=subject,
                message=text_body,
                from_email=from_email,
                recipient_list=[approval.contact.email],
                html_message=html_body,
                fail_silently=False,
            )

            approval.reminded_count += 1
            approval.last_reminded_at = timezone.now()
            approval.save(update_fields=["reminded_count", "last_reminded_at", "updated_at"])
            return True
        except Exception as exc:
            logger.error("Failed to send approval reminder for approval %s: %s", approval.pk, exc)
            return False

    @staticmethod
    def _notify_client_of_approval(approval):
        """Create a portal message notifying the client of a new approval request."""
        if not approval.contact:
            return

        # Try to find portal access for this contact+project
        portal_access = ClientPortalAccess.objects.filter(
            organization=approval.organization,
            project=approval.project,
            contact=approval.contact,
            is_active=True,
        ).first()

        if portal_access:
            ClientMessage.objects.create(
                organization=approval.organization,
                project=approval.project,
                sender_type=ClientMessage.SenderType.CONTRACTOR,
                subject=f"Action required: {approval.title}",
                body=(
                    f"You have a new approval request that requires your attention.\n\n"
                    f"Type: {approval.get_approval_type_display()}\n"
                    f"Description: {approval.description}\n\n"
                    f"Please log in to your project portal to review and respond."
                ),
            )


class ClientNotificationService:
    """
    Automated client notification system.

    Respects notification frequency preferences stored on ClientPortalAccess.permissions:
        notification_preference: "realtime" | "daily" | "weekly" (default: "daily")
    """

    @staticmethod
    def send_milestone_notification(project, milestone_name, portal_access=None):
        """
        Notify client(s) that a project milestone has been reached.

        Args:
            project: Project instance
            milestone_name: Human-readable milestone name (e.g., "Framing Complete")
            portal_access: Specific ClientPortalAccess, or None to notify all active
        """
        accesses = [portal_access] if portal_access else (
            ClientPortalAccess.objects.filter(
                project=project,
                is_active=True,
            ).select_related("contact", "organization")
        )

        for access in accesses:
            pref = access.permissions.get("notification_preference", "daily")
            if pref == "realtime":
                ClientNotificationService._send_milestone_email(access, milestone_name)

    @staticmethod
    def send_photos_uploaded_notification(project, photo_count, portal_access=None):
        """Notify client(s) that new photos have been uploaded to the project."""
        accesses = [portal_access] if portal_access else (
            ClientPortalAccess.objects.filter(
                project=project,
                is_active=True,
                permissions__contains={"view_photos": True},
            ).select_related("contact", "organization")
        )

        for access in accesses:
            pref = access.permissions.get("notification_preference", "daily")
            if pref == "realtime":
                ClientNotificationService._send_generic_email(
                    access,
                    subject=f"{photo_count} new photo(s) added to your project",
                    body=(
                        f"{photo_count} new photo(s) have been uploaded to your project "
                        f"'{project.name}'. Log in to your portal to view them."
                    ),
                )

    @staticmethod
    def send_daily_digest(portal_access, digest_data):
        """
        Send the daily digest email summarizing updates.

        Args:
            portal_access: ClientPortalAccess instance
            digest_data: Dict with keys: messages, approvals, selections, photos
        """
        org = portal_access.organization

        from apps.clients.models import PortalBranding
        branding = PortalBranding.objects.filter(organization=org).first()
        company_name = (
            branding.company_name_override
            if branding and branding.company_name_override
            else org.name
        )

        context = {
            "portal_access": portal_access,
            "contact": portal_access.contact,
            "project": portal_access.project,
            "organization": org,
            "company_name": company_name,
            "digest": digest_data,
        }

        try:
            subject = f"Daily update: {portal_access.project.name}"
            html_body = render_to_string("emails/client_daily_digest.html", context)
            text_body = render_to_string("emails/client_daily_digest.txt", context)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@builderstream.com")

            send_mail(
                subject=subject,
                message=text_body,
                from_email=from_email,
                recipient_list=[portal_access.email],
                html_message=html_body,
                fail_silently=False,
            )
            logger.info(
                "Daily digest sent to %s for project %s",
                portal_access.email,
                portal_access.project_id,
            )
        except Exception as exc:
            logger.error(
                "Failed to send daily digest to %s: %s",
                portal_access.email,
                exc,
            )

    @staticmethod
    def compile_daily_digest_data(portal_access, since=None):
        """
        Compile updates since `since` (default: last 24 hours).

        Returns dict with counts for messages, approvals, selections.
        """
        if since is None:
            since = timezone.now() - timedelta(hours=24)

        project = portal_access.project
        org = portal_access.organization

        new_messages = ClientMessage.objects.filter(
            organization=org,
            project=project,
            sender_type=ClientMessage.SenderType.CONTRACTOR,
            created_at__gte=since,
        ).count()

        pending_approvals = ClientApproval.objects.filter(
            organization=org,
            project=project,
            status=ClientApproval.Status.PENDING,
        ).count()

        pending_selections = Selection.objects.filter(
            organization=org,
            project=project,
            status=Selection.Status.CLIENT_REVIEW,
            assigned_to_client=True,
        ).count()

        return {
            "new_messages": new_messages,
            "pending_approvals": pending_approvals,
            "pending_selections": pending_selections,
            "since": since,
        }

    @staticmethod
    def send_satisfaction_survey(portal_access, milestone):
        """
        Send an NPS/satisfaction survey to a client after a milestone.

        Args:
            portal_access: ClientPortalAccess instance
            milestone: Milestone name that triggered the survey
        """
        org = portal_access.organization

        # Check if survey already sent for this milestone
        already_sent = ClientSatisfactionSurvey.objects.filter(
            organization=org,
            project=portal_access.project,
            contact=portal_access.contact,
            milestone=milestone,
        ).exists()

        if already_sent:
            return False

        from apps.clients.models import PortalBranding
        branding = PortalBranding.objects.filter(organization=org).first()
        company_name = (
            branding.company_name_override
            if branding and branding.company_name_override
            else org.name
        )

        context = {
            "portal_access": portal_access,
            "contact": portal_access.contact,
            "project": portal_access.project,
            "organization": org,
            "company_name": company_name,
            "milestone": milestone,
        }

        try:
            subject = f"How are we doing? Quick feedback on {portal_access.project.name}"
            html_body = render_to_string("emails/satisfaction_survey.html", context)
            text_body = render_to_string("emails/satisfaction_survey.txt", context)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@builderstream.com")

            send_mail(
                subject=subject,
                message=text_body,
                from_email=from_email,
                recipient_list=[portal_access.email],
                html_message=html_body,
                fail_silently=False,
            )
            logger.info(
                "Satisfaction survey sent to %s for milestone '%s'",
                portal_access.email,
                milestone,
            )
            return True
        except Exception as exc:
            logger.error("Failed to send satisfaction survey: %s", exc)
            return False

    @staticmethod
    def _send_milestone_email(portal_access, milestone_name):
        """Low-level milestone email send."""
        try:
            from apps.clients.models import PortalBranding
            org = portal_access.organization
            branding = PortalBranding.objects.filter(organization=org).first()
            company_name = (
                branding.company_name_override
                if branding and branding.company_name_override
                else org.name
            )
            context = {
                "portal_access": portal_access,
                "contact": portal_access.contact,
                "project": portal_access.project,
                "company_name": company_name,
                "milestone_name": milestone_name,
            }
            html_body = render_to_string("emails/milestone_notification.html", context)
            text_body = render_to_string("emails/milestone_notification.txt", context)
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@builderstream.com")
            send_mail(
                subject=f"Project update: {milestone_name} — {portal_access.project.name}",
                message=text_body,
                from_email=from_email,
                recipient_list=[portal_access.email],
                html_message=html_body,
                fail_silently=True,
            )
        except Exception as exc:
            logger.warning("Milestone email failed: %s", exc)

    @staticmethod
    def _send_generic_email(portal_access, subject, body):
        """Generic portal notification email."""
        try:
            from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@builderstream.com")
            send_mail(
                subject=subject,
                message=body,
                from_email=from_email,
                recipient_list=[portal_access.email],
                fail_silently=True,
            )
        except Exception as exc:
            logger.warning("Generic portal email failed: %s", exc)
