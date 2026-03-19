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
        lines = list(purchase_order.line_items.all())
        if not lines:
            return

        for line_item in lines:
            qty = received_quantities.get(str(line_item.pk))
            if qty is not None:
                line_item.received_quantity = Decimal(str(qty))
                line_item.save(update_fields=["received_quantity", "updated_at"])

        # Refresh from DB to get updated received_quantity values
        lines = list(purchase_order.line_items.all())
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


class AIABillingService:
    """AIA G702 Application for Payment + G703 Continuation Sheet PDF generation.

    The AIA (American Institute of Architects) G702/G703 is the standard form
    used in the construction industry for progress billing on contracts.

    Fields used from Invoice:
        scheduled_value            — Original contract amount
        work_completed_previous    — Work completed through previous applications
        work_completed_this_period — Work completed this billing period
        retainage_percent          — Retainage percentage held
        retainage_amount           — Computed retainage held to date
        total                      — Contract sum to date (stored materials included)
        amount_paid                — Amount previously certified
        balance_due                — Current payment due
        notes                      — Architect's certification notes
    """

    @staticmethod
    def _build_aia_computed(invoice) -> dict:
        """Compute all derived AIA G702 fields from the invoice model fields."""
        from decimal import Decimal

        scheduled = invoice.scheduled_value or Decimal("0.00")
        prev = invoice.work_completed_previous or Decimal("0.00")
        this_period = invoice.work_completed_this_period or Decimal("0.00")
        stored = Decimal("0.00")  # stored_materials — reserved field

        total_completed = prev + this_period + stored
        pct_complete = (total_completed / scheduled * 100) if scheduled else Decimal("0.00")
        retainage = (total_completed * invoice.retainage_percent / 100) if invoice.retainage_percent else invoice.retainage_amount or Decimal("0.00")
        balance_to_finish = scheduled - total_completed
        current_due = total_completed - retainage - (invoice.amount_paid or Decimal("0.00"))

        return {
            "scheduled_value": scheduled,
            "work_completed_previous": prev,
            "work_completed_this_period": this_period,
            "stored_materials": stored,
            "total_completed": total_completed,
            "pct_complete": pct_complete.quantize(Decimal("0.01")),
            "retainage": retainage,
            "balance_to_finish": balance_to_finish,
            "current_due": current_due,
        }

    @staticmethod
    def generate_g702(invoice) -> "BytesIO":
        """Generate AIA G702 Application for Payment PDF. Returns BytesIO."""
        from io import BytesIO
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        computed = AIABillingService._build_aia_computed(invoice)
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter,
            topMargin=0.5 * inch, bottomMargin=0.5 * inch,
            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        header_style = ParagraphStyle("AIA_Header", parent=styles["Heading1"], fontSize=14, spaceAfter=4)
        label_style = ParagraphStyle("AIA_Label", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
        value_style = ParagraphStyle("AIA_Value", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold")
        small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8)

        def fmt(val):
            try:
                return f"${float(val):,.2f}"
            except Exception:
                return str(val)

        story = []

        # ── Header ──
        story.append(Paragraph("AIA Document G702™", header_style))
        story.append(Paragraph("Application and Certificate for Payment", styles["Heading2"]))
        story.append(Spacer(1, 0.15 * inch))

        # ── Project Info ──
        project = invoice.project
        org = invoice.organization
        info_data = [
            ["Project:", project.name if project else "—", "Application No:", invoice.invoice_number],
            ["Owner:", str(project.client_name or "—") if project else "—", "Period To:", str(invoice.due_date or "—")],
            ["Contractor:", org.name if org else "—", "Contract Date:", str(invoice.issue_date or "—")],
        ]
        info_table = Table(info_data, colWidths=[1.2*inch, 2.8*inch, 1.2*inch, 2.0*inch])
        info_table.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # ── Schedule of Values Summary ──
        story.append(Paragraph("CONTRACTOR'S APPLICATION FOR PAYMENT", styles["Heading3"]))
        story.append(Spacer(1, 0.08 * inch))

        summary_data = [
            ["", "Amount"],
            ["1. Original Contract Sum", fmt(computed["scheduled_value"])],
            ["2. Work Completed From Previous Applications (D + E)", fmt(computed["work_completed_previous"])],
            ["3. Work Completed This Period (Column D)", fmt(computed["work_completed_this_period"])],
            ["4. Stored Materials (Column F)", fmt(computed["stored_materials"])],
            ["5. Total Completed and Stored to Date (Lines 2+3+4)", fmt(computed["total_completed"])],
            [f"6. Retainage ({invoice.retainage_percent}%)", fmt(computed["retainage"])],
            ["7. Total Earned Less Retainage (Line 5 Less Line 6)", fmt(computed["total_completed"] - computed["retainage"])],
            ["8. Less Previous Certificates for Payment", fmt(invoice.amount_paid or 0)],
            ["9. CURRENT PAYMENT DUE", fmt(computed["current_due"])],
            ["10. Balance to Finish, Including Retainage (Line 1 Less Line 7)", fmt(computed["balance_to_finish"] + computed["retainage"])],
        ]
        col_w = [5.5 * inch, 1.75 * inch]
        sum_table = Table(summary_data, colWidths=col_w)
        sum_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 9), (1, 9), "Helvetica-Bold"),
            ("BACKGROUND", (0, 9), (-1, 9), colors.HexColor("#e8f4e8")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (0, -1), 6),
        ]))
        story.append(sum_table)
        story.append(Spacer(1, 0.25 * inch))

        # ── Certification block ──
        story.append(Paragraph("ARCHITECT'S CERTIFICATE FOR PAYMENT", styles["Heading3"]))
        story.append(Spacer(1, 0.05 * inch))
        cert_text = (
            "In accordance with the Contract Documents, based on on-site observations and the data comprising "
            "the above application, the Architect certifies to the Owner that to the best of the Architect's "
            "knowledge, information, and belief the Work has progressed as indicated, the quality of the Work "
            "is in accordance with the Contract Documents, and the Contractor is entitled to payment of the "
            "AMOUNT CERTIFIED."
        )
        story.append(Paragraph(cert_text, small))
        story.append(Spacer(1, 0.15 * inch))

        cert_data = [
            ["AMOUNT CERTIFIED", fmt(computed["current_due"])],
            ["Architect:", ""],
            ["Date:", ""],
        ]
        cert_table = Table(cert_data, colWidths=[2.5 * inch, 4.75 * inch])
        cert_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (1, 0), (1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(cert_table)

        if invoice.notes:
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph(f"Notes: {invoice.notes}", small))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_g703(invoice) -> "BytesIO":
        """Generate AIA G703 Continuation Sheet PDF. Returns BytesIO.

        G703 breaks down the scheduled value by line item (InvoiceLineItem),
        showing % complete, work completed, stored materials, and balance.
        """
        from io import BytesIO
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=landscape(letter),
            topMargin=0.5 * inch, bottomMargin=0.5 * inch,
            leftMargin=0.5 * inch, rightMargin=0.5 * inch,
        )
        styles = getSampleStyleSheet()
        small = ParagraphStyle("small", parent=styles["Normal"], fontSize=7)

        story = []
        story.append(Paragraph("AIA Document G703™ — Continuation Sheet", styles["Heading2"]))
        story.append(Paragraph(
            f"Application No: {invoice.invoice_number}  |  Project: {invoice.project.name if invoice.project else '—'}",
            styles["Normal"],
        ))
        story.append(Spacer(1, 0.15 * inch))

        col_headers = [
            "A\nItem No.", "B\nDescription of Work", "C\nScheduled\nValue",
            "D\nWork Completed\nFrom Prev App",
            "E\nWork Completed\nThis Period",
            "F\nMaterials\nPresently Stored",
            "G\nTotal Completed\n& Stored (D+E+F)",
            "H\n%\n(G/C)",
            "I\nBalance\nto Finish",
            "J\nRetainage",
        ]

        rows = [col_headers]
        line_items = list(invoice.line_items.all())
        grand_scheduled = grand_total = grand_bal = grand_ret = 0

        for i, item in enumerate(line_items, 1):
            sched = float(item.unit_price * item.quantity) if item.unit_price and item.quantity else 0
            completed_prev = 0
            completed_this = float(item.total_price or sched)
            stored = 0
            total_g = completed_prev + completed_this + stored
            pct = f"{(total_g / sched * 100):.1f}%" if sched else "0%"
            balance = sched - total_g
            ret_rate = float(invoice.retainage_percent or 0) / 100
            ret = total_g * ret_rate

            grand_scheduled += sched
            grand_total += total_g
            grand_bal += balance
            grand_ret += ret

            rows.append([
                str(i),
                item.description[:40] if item.description else "",
                f"${sched:,.2f}",
                f"${completed_prev:,.2f}",
                f"${completed_this:,.2f}",
                f"${stored:,.2f}",
                f"${total_g:,.2f}",
                pct,
                f"${balance:,.2f}",
                f"${ret:,.2f}",
            ])

        # Totals row
        rows.append([
            "", "TOTALS",
            f"${grand_scheduled:,.2f}", "", "",  "",
            f"${grand_total:,.2f}", "",
            f"${grand_bal:,.2f}",
            f"${grand_ret:,.2f}",
        ])

        col_w = [0.4*inch, 2.8*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.0*inch, 0.55*inch, 1.0*inch, 1.0*inch]
        t = Table(rows, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0f0f0")),
        ]))
        story.append(t)

        doc.build(story)
        buffer.seek(0)
        return buffer


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


class CurrencyService:
    """Exchange rate fetching and amount conversion with Redis caching."""

    CACHE_TTL = 3600  # 1 hour
    SUPPORTED = {
        "USD", "EUR", "GBP", "CAD", "AUD", "MXN", "JPY", "CHF",
        "SEK", "NOK", "DKK", "NZD", "SGD", "HKD", "BRL", "INR",
    }

    @staticmethod
    def _cache_key(from_ccy: str, to_ccy: str, date_str: str) -> str:
        return f"fx:{from_ccy}:{to_ccy}:{date_str}"

    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str, rate_date=None):
        """Return exchange rate with 1-hour Redis cache.

        Falls back to 1.0 if the Open Exchange Rates API key is not configured
        so that the platform remains functional without external dependencies.
        """
        from decimal import Decimal
        from django.core.cache import cache
        from django.conf import settings
        import urllib.request, json as json_mod
        from django.utils import timezone as tz

        if from_currency == to_currency:
            return Decimal("1.0")

        date_str = (rate_date or tz.now().date()).isoformat()
        cache_key = cls._cache_key(from_currency, to_currency, date_str)
        cached = cache.get(cache_key)
        if cached is not None:
            return Decimal(str(cached))

        api_key = getattr(settings, "OPEN_EXCHANGE_RATES_API_KEY", "")
        if not api_key:
            logger.warning(
                "OPEN_EXCHANGE_RATES_API_KEY not set — using 1:1 rate for %s→%s",
                from_currency, to_currency,
            )
            return Decimal("1.0")

        try:
            url = f"https://openexchangerates.org/api/historical/{date_str}.json?app_id={api_key}&base=USD&symbols={from_currency},{to_currency}"
            with urllib.request.urlopen(url, timeout=5) as resp:
                payload = json_mod.loads(resp.read())
            rates = payload.get("rates", {})
            from_rate = Decimal(str(rates.get(from_currency, 1)))
            to_rate = Decimal(str(rates.get(to_currency, 1)))
            rate = to_rate / from_rate
            cache.set(cache_key, str(rate), CurrencyService.CACHE_TTL)
            return rate
        except Exception as exc:
            logger.error("Currency fetch failed (%s→%s): %s", from_currency, to_currency, exc)
            return Decimal("1.0")

    @classmethod
    def convert(cls, amount, from_currency: str, to_currency: str, rate_date=None):
        from decimal import Decimal
        amount = Decimal(str(amount))
        rate = cls.get_exchange_rate(from_currency, to_currency, rate_date)
        return (amount * rate).quantize(Decimal("0.01"))

    @classmethod
    def format_amount(cls, amount, currency: str = "USD") -> str:
        try:
            from babel.numbers import format_currency
            return format_currency(amount, currency, locale="en_US")
        except Exception:
            return f"{currency} {amount:,.2f}"

# -- DunningService -----------------------------------------------------------

class DunningService:
    """Process overdue invoices and trigger configured dunning rules."""

    @staticmethod
    def process_overdue_invoices():
        """Daily task: find overdue invoices, trigger matching rules not yet fired."""
        import logging
        from django.utils import timezone
        from .models import Invoice, DunningRule, DunningEvent

        logger = logging.getLogger(__name__)
        now = timezone.now().date()

        # Only SENT / VIEWED / PARTIAL invoices with a past due_date
        overdue_invoices = Invoice.objects.unscoped().filter(
            status__in=["sent", "viewed", "partial"],
            due_date__lt=now,
        ).select_related("project", "client", "organization")

        for invoice in overdue_invoices:
            days_past_due = (now - invoice.due_date).days
            rules = DunningRule.objects.for_organization(invoice.organization).filter(
                is_active=True,
                days_past_due__lte=days_past_due,
            ).order_by("days_past_due")

            for rule in rules:
                # Check if this rule has already been triggered for this invoice
                already_triggered = DunningEvent.objects.filter(
                    invoice=invoice,
                    rule=rule,
                ).exists()
                if already_triggered:
                    continue

                success = DunningService._execute_rule(invoice, rule)
                DunningEvent.objects.create(
                    invoice=invoice,
                    rule=rule,
                    action_taken=rule.action_type,
                    success=success,
                )
                logger.info(
                    "Dunning rule %s triggered for invoice %s (days_past_due=%d)",
                    rule.name, invoice.invoice_number, days_past_due,
                )

    @staticmethod
    def _execute_rule(invoice, rule):
        """Execute the dunning action. Returns True on success."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            if rule.action_type == "email_reminder":
                DunningService._send_email_reminder(invoice, rule)
            elif rule.action_type == "suspend_portal":
                DunningService._suspend_portal_access(invoice)
            elif rule.action_type == "flag_escalation":
                logger.warning(
                    "ESCALATION REQUIRED: Invoice %s is %s days past due  -  org %s",
                    invoice.invoice_number,
                    (timezone.now().date() - invoice.due_date).days,
                    invoice.organization.name,
                )
            return True
        except Exception:
            logger.exception("Dunning rule %s failed for invoice %s", rule.pk, invoice.pk)
            return False

    @staticmethod
    def _send_email_reminder(invoice, rule):
        """Send email reminder. Stubs email sending  -  full integration requires email service."""
        import logging
        logger = logging.getLogger(__name__)

        client_name = invoice.client.first_name + " " + invoice.client.last_name if invoice.client else "Client"
        body = rule.email_body.replace("{{invoice_number}}", invoice.invoice_number)
        body = body.replace("{{balance_due}}", str(invoice.balance_due))
        body = body.replace("{{client_name}}", client_name)
        body = body.replace("{{due_date}}", str(invoice.due_date))

        logger.info(
            "[DUNNING EMAIL] To: %s | Subject: %s | Invoice: %s | Balance: %s",
            invoice.sent_to_email or (invoice.client.email if invoice.client else "?"),
            rule.email_subject,
            invoice.invoice_number,
            invoice.balance_due,
        )
        # Full implementation: call EmailService.send(to=email, subject=..., body=...)

    @staticmethod
    def _suspend_portal_access(invoice):
        """Flag the invoice so portal access is blocked."""
        invoice.status = "overdue"
        invoice.save(update_fields=["status"])
