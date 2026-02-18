"""Financial Management Suite — business logic services."""
import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class JobCostingService:
    """Real-time job costing and budget variance tracking."""

    @staticmethod
    def get_project_cost_summary(project):
        """Return budget vs actual summary across all cost codes for a project."""
        from .models import Budget, Expense

        budget_lines = Budget.objects.filter(project=project).select_related("cost_code")
        expenses = Expense.objects.filter(
            project=project, approval_status="approved"
        ).values("cost_code_id").annotate(total=Sum("amount"))
        expense_by_code = {str(e["cost_code_id"]): e["total"] for e in expenses}

        summary = []
        total_budgeted = Decimal("0.00")
        total_actual = Decimal("0.00")

        for line in budget_lines:
            code_id = str(line.cost_code_id) if line.cost_code_id else None
            actual = expense_by_code.get(code_id, Decimal("0.00"))
            variance = line.budgeted_amount - actual
            variance_pct = (variance / line.budgeted_amount * 100) if line.budgeted_amount else Decimal("0.00")
            summary.append({
                "budget_line_id": str(line.pk),
                "description": line.description,
                "cost_code": str(line.cost_code) if line.cost_code else None,
                "budgeted_amount": float(line.budgeted_amount),
                "actual_amount": float(actual),
                "variance_amount": float(variance),
                "variance_percent": float(variance_pct),
            })
            total_budgeted += line.budgeted_amount
            total_actual += actual

        total_variance = total_budgeted - total_actual
        total_variance_pct = (
            (total_variance / total_budgeted * 100) if total_budgeted else Decimal("0.00")
        )

        return {
            "project_id": str(project.pk),
            "project_name": str(project),
            "total_budgeted": float(total_budgeted),
            "total_actual": float(total_actual),
            "total_variance": float(total_variance),
            "total_variance_percent": float(total_variance_pct),
            "lines": summary,
        }

    @staticmethod
    def update_budget_actuals(project):
        """Sync actual_amount on all Budget lines from approved Expenses."""
        from .models import Budget, Expense

        budget_lines = Budget.objects.filter(project=project)
        for line in budget_lines:
            actual = Expense.objects.filter(
                project=project,
                cost_code=line.cost_code,
                approval_status="approved",
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            if line.actual_amount != actual:
                line.actual_amount = actual
                line.save(update_fields=["actual_amount", "variance_amount", "variance_percent", "updated_at"])

    @staticmethod
    def get_cash_flow_forecast(organization, months=6):
        """Simple cash flow forecast: invoices due vs expenses expected per month."""
        from .models import Invoice, Expense

        today = date.today()
        result = []

        for i in range(months):
            month_start = (today.replace(day=1) + timedelta(days=32 * i)).replace(day=1)
            if i == 0:
                month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            else:
                # next month last day
                next_m = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
                month_end = next_m - timedelta(days=1)

            invoiced = Invoice.objects.filter(
                organization=organization,
                due_date__gte=month_start,
                due_date__lte=month_end,
                status__in=["sent", "viewed", "partial", "overdue"],
            ).aggregate(total=Sum("balance_due"))["total"] or Decimal("0.00")

            paid = Invoice.objects.filter(
                organization=organization,
                paid_date__gte=month_start,
                paid_date__lte=month_end,
                status="paid",
            ).aggregate(total=Sum("total"))["total"] or Decimal("0.00")

            expenses = Expense.objects.filter(
                organization=organization,
                expense_date__gte=month_start,
                expense_date__lte=month_end,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            result.append({
                "month": month_start.strftime("%Y-%m"),
                "invoices_due": float(invoiced),
                "payments_received": float(paid),
                "expenses_incurred": float(expenses),
                "net": float(paid - expenses),
            })

        return result


class InvoicingService:
    """Invoice creation, numbering, sending, and payment recording."""

    @staticmethod
    def generate_invoice_number(organization):
        """Auto-increment: INV-{YEAR}-{SEQ:04d} per org per year."""
        from .models import Invoice

        current_year = timezone.now().year
        prefix = f"INV-{current_year}-"

        last = (
            Invoice.objects.filter(
                organization=organization,
                invoice_number__startswith=prefix,
            )
            .order_by("-invoice_number")
            .first()
        )
        if last:
            try:
                seq = int(last.invoice_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1

        return f"{prefix}{seq:04d}"

    @staticmethod
    def recalculate_invoice(invoice):
        """Recalculate invoice totals from line items and save."""
        invoice.recalculate_totals()
        invoice.save(update_fields=[
            "subtotal", "tax_amount", "retainage_amount",
            "total", "balance_due", "updated_at",
        ])

    @staticmethod
    def record_payment(invoice, amount, payment_date, payment_method="check",
                       reference_number="", notes="", recorded_by=None):
        """Create a Payment record and update invoice status."""
        from .models import Payment

        payment = Payment.objects.create(
            organization=invoice.organization,
            invoice=invoice,
            project=invoice.project,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            recorded_by=recorded_by,
        )

        # Update invoice amount_paid and status
        total_paid = invoice.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        invoice.amount_paid = total_paid
        invoice.balance_due = invoice.total - total_paid

        if invoice.balance_due <= 0:
            invoice.status = "paid"
            invoice.paid_date = payment_date
        elif total_paid > 0:
            invoice.status = "partial"

        invoice.save(update_fields=["amount_paid", "balance_due", "status", "paid_date", "updated_at"])
        logger.info("Payment %s recorded for invoice %s", payment.pk, invoice.invoice_number)
        return payment

    @staticmethod
    def mark_sent(invoice, sent_to_email, user=None):
        """Mark invoice as sent and record timestamp."""
        invoice.status = "sent"
        invoice.sent_at = timezone.now()
        invoice.sent_to_email = sent_to_email
        invoice.save(update_fields=["status", "sent_at", "sent_to_email", "updated_at"])

    @staticmethod
    def check_and_mark_overdue(organization):
        """Mark all unpaid invoices past due_date as overdue."""
        from .models import Invoice

        today = date.today()
        updated = Invoice.objects.filter(
            organization=organization,
            status__in=["sent", "viewed", "partial"],
            due_date__lt=today,
        ).update(status="overdue")
        logger.info("Marked %d invoices overdue for org %s", updated, organization)
        return updated


class ChangeOrderService:
    """Change order management and approval workflow."""

    @staticmethod
    def get_next_co_number(project):
        """Auto-increment CO number per project."""
        from .models import ChangeOrder
        from django.db.models import Max

        max_num = ChangeOrder.objects.filter(project=project).aggregate(m=Max("number"))["m"]
        return (max_num or 0) + 1

    @staticmethod
    def submit_change_order(change_order, user):
        """Submit CO to client for review."""
        change_order.status = "submitted"
        change_order.submitted_date = date.today()
        change_order.save(update_fields=["status", "submitted_date", "updated_at"])
        logger.info("CO #%s submitted for project %s by %s", change_order.number, change_order.project, user)

    @staticmethod
    def approve_change_order(change_order, approved_by_name, user):
        """Approve a CO and update the project's estimated value."""
        change_order.status = "approved"
        change_order.approved_date = date.today()
        change_order.approved_by_name = approved_by_name
        change_order.save(update_fields=["status", "approved_date", "approved_by_name", "updated_at"])

        # Adjust project estimated value
        project = change_order.project
        if project.estimated_value is not None:
            project.estimated_value += change_order.cost_impact
            project.save(update_fields=["estimated_value", "updated_at"])

        logger.info("CO #%s approved for project %s", change_order.number, change_order.project)

    @staticmethod
    def reject_change_order(change_order, reason, user):
        """Reject a CO."""
        change_order.status = "rejected"
        change_order.rejected_date = date.today()
        change_order.reason = reason
        change_order.save(update_fields=["status", "rejected_date", "reason", "updated_at"])

    @staticmethod
    def recalculate_cost_impact(change_order):
        """Sum line items to update cost_impact on the CO."""
        total = change_order.line_items.aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")
        change_order.cost_impact = total
        change_order.save(update_fields=["cost_impact", "updated_at"])


class PurchaseOrderService:
    """Purchase order creation and receiving workflow."""

    @staticmethod
    def generate_po_number(organization):
        """Auto-increment: PO-{YEAR}-{SEQ:04d} per org per year."""
        from .models import PurchaseOrder

        current_year = timezone.now().year
        prefix = f"PO-{current_year}-"

        last = (
            PurchaseOrder.objects.filter(
                organization=organization,
                po_number__startswith=prefix,
            )
            .order_by("-po_number")
            .first()
        )
        if last:
            try:
                seq = int(last.po_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1

        return f"{prefix}{seq:04d}"

    @staticmethod
    def recalculate_po_totals(purchase_order):
        """Recalculate PO totals from line items and save."""
        purchase_order.recalculate_totals()
        purchase_order.save(update_fields=["subtotal", "total", "updated_at"])

    @staticmethod
    def receive_line_items(purchase_order, received_quantities, user=None):
        """Record received quantities per line item.

        received_quantities: dict of {line_item_id: quantity_received}
        """
        for line_item in purchase_order.line_items.all():
            qty = received_quantities.get(str(line_item.pk))
            if qty is not None:
                line_item.received_quantity = Decimal(str(qty))
                line_item.save(update_fields=["received_quantity", "updated_at"])

        # Update PO status based on receipt completeness
        lines = list(purchase_order.line_items.all())
        if not lines:
            return

        all_received = all(line.received_quantity >= line.quantity for line in lines)
        any_received = any(line.received_quantity > 0 for line in lines)

        if all_received:
            purchase_order.status = "received"
            purchase_order.actual_delivery_date = date.today()
            purchase_order.save(update_fields=["status", "actual_delivery_date", "updated_at"])
        elif any_received:
            purchase_order.status = "partial"
            purchase_order.save(update_fields=["status", "updated_at"])

        logger.info("PO %s receiving recorded", purchase_order.po_number)


class InvoiceExportService:
    """Invoice PDF generation and email delivery."""

    @staticmethod
    def generate_invoice_pdf(invoice):
        """Generate a professional invoice PDF using reportlab. Returns BytesIO."""
        from io import BytesIO

        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.75 * inch,
            rightMargin=0.75 * inch,
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=styles["Heading1"],
            fontSize=22,
            textColor=colors.HexColor("#1e40af"),
            spaceAfter=6,
            alignment=TA_CENTER,
        )
        right_style = ParagraphStyle(
            "Right", parent=styles["Normal"], alignment=TA_RIGHT
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=11,
            textColor=colors.HexColor("#1e40af"),
            spaceBefore=10,
            spaceAfter=4,
        )

        # ── Header ──────────────────────────────────────────────────────────
        story.append(Paragraph(invoice.organization.name, title_style))
        story.append(Spacer(1, 0.1 * inch))

        # Two-column: bill-to on left, invoice meta on right
        right_lines = [
            f"<b>INVOICE #{invoice.invoice_number}</b>",
            f"Type: {invoice.get_invoice_type_display()}",
            f"Status: {invoice.get_status_display()}",
        ]
        if invoice.issue_date:
            right_lines.append(f"Issue Date: {invoice.issue_date.strftime('%B %d, %Y')}")
        if invoice.due_date:
            right_lines.append(f"Due Date: {invoice.due_date.strftime('%B %d, %Y')}")

        left_lines = []
        if invoice.client:
            left_lines += [
                "<b>Bill To:</b>",
                f"{invoice.client.first_name} {invoice.client.last_name}",
                invoice.client.email or "",
            ]
            if invoice.client.phone:
                left_lines.append(invoice.client.phone)
        left_lines += ["", f"<b>Project:</b> {invoice.project}"]

        header_table = Table(
            [[
                Paragraph("<br/>".join(left_lines), styles["Normal"]),
                Paragraph("<br/>".join(right_lines), right_style),
            ]],
            colWidths=[3.5 * inch, 3 * inch],
        )
        header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(header_table)
        story.append(Spacer(1, 0.3 * inch))

        # ── Line Items ───────────────────────────────────────────────────────
        story.append(Paragraph("Invoice Details", heading_style))
        table_data = [["Description", "Qty", "Unit", "Unit Price", "Total"]]
        for item in invoice.line_items.all():
            table_data.append([
                Paragraph(item.description, styles["Normal"]),
                str(item.quantity),
                item.unit or "",
                f"${item.unit_price:,.2f}",
                f"${item.line_total:,.2f}",
            ])

        table_data.append(["", "", "", "", ""])  # spacer row
        table_data.append([
            "", "", "",
            Paragraph("<b>Subtotal:</b>", styles["Normal"]),
            f"${invoice.subtotal:,.2f}",
        ])
        if invoice.tax_rate:
            table_data.append([
                "", "", "",
                Paragraph(f"<b>Tax ({invoice.tax_rate}%):</b>", styles["Normal"]),
                f"${invoice.tax_amount:,.2f}",
            ])
        if invoice.retainage_percent:
            table_data.append([
                "", "", "",
                Paragraph(f"<b>Retainage ({invoice.retainage_percent}%):</b>", styles["Normal"]),
                f"(${invoice.retainage_amount:,.2f})",
            ])
        if invoice.amount_paid > 0:
            table_data.append([
                "", "", "",
                Paragraph("<b>Amount Paid:</b>", styles["Normal"]),
                f"(${invoice.amount_paid:,.2f})",
            ])
        table_data.append([
            "", "", "",
            Paragraph("<b>BALANCE DUE:</b>", styles["Heading3"]),
            Paragraph(f"<b>${invoice.balance_due:,.2f}</b>", styles["Heading3"]),
        ])

        line_count = invoice.line_items.count()
        tbl = Table(
            table_data,
            colWidths=[3.25 * inch, 0.5 * inch, 0.5 * inch, 1.5 * inch, 1 * inch],
        )
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, line_count), 0.5, colors.lightgrey),
            ("LINEABOVE", (3, -1), (-1, -1), 1.5, colors.black),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.4 * inch))

        # ── Terms / Notes ────────────────────────────────────────────────────
        if invoice.terms:
            story.append(Paragraph("<b>Terms &amp; Payment Instructions</b>", heading_style))
            story.append(Paragraph(invoice.terms, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

        if invoice.notes:
            story.append(Paragraph("<b>Notes</b>", heading_style))
            story.append(Paragraph(invoice.notes, styles["Normal"]))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def send_invoice_by_email(invoice, recipient_email, public_url):
        """Send invoice PDF by email. Generates PDF inline (no file storage required)."""
        from django.conf import settings as django_settings
        from django.core.mail import EmailMessage

        pdf_buffer = InvoiceExportService.generate_invoice_pdf(invoice)

        client_name = (
            invoice.client.first_name if invoice.client else "Valued Client"
        )
        due_str = (
            f"by {invoice.due_date.strftime('%B %d, %Y')}"
            if invoice.due_date
            else "upon receipt"
        )

        subject = f"Invoice #{invoice.invoice_number} from {invoice.organization.name}"
        body = (
            f"Dear {client_name},\n\n"
            f"Please find attached invoice #{invoice.invoice_number} "
            f"for ${invoice.balance_due:,.2f} due {due_str}.\n\n"
            f"You can also view and pay your invoice online:\n{public_url}\n\n"
            f"Thank you for your business.\n\n"
            f"Best regards,\n{invoice.organization.name}"
        )

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach(
            f"Invoice_{invoice.invoice_number}.pdf",
            pdf_buffer.read(),
            "application/pdf",
        )
        email.send(fail_silently=False)
        logger.info(
            "Invoice email sent: %s → %s", invoice.invoice_number, recipient_email
        )


class QuickBooksSyncService:
    """Stub for QuickBooks / Xero integration hooks (Phase 2 feature)."""

    @staticmethod
    def sync_invoice_to_quickbooks(invoice):
        """Push invoice to QuickBooks Online via API (stub)."""
        logger.info(
            "QuickBooks sync stub: invoice %s — QB integration not yet configured",
            invoice.invoice_number,
        )
        return {"status": "stub", "invoice_number": invoice.invoice_number}

    @staticmethod
    def sync_expense_to_quickbooks(expense):
        """Push expense to QuickBooks Online via API (stub)."""
        logger.info(
            "QuickBooks sync stub: expense %s — QB integration not yet configured",
            expense.pk,
        )
        return {"status": "stub", "expense_id": str(expense.pk)}

    @staticmethod
    def pull_vendor_list():
        """Pull vendor list from QuickBooks (stub)."""
        logger.info("QuickBooks sync stub: pull_vendor_list — QB integration not yet configured")
        return []
