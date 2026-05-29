"""Payroll & Workforce Management services."""
import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone as django_tz

logger = logging.getLogger(__name__)

# ── Tax rate stubs ──────────────────────────────────────────────────────────
# In production these would integrate with a payroll tax service (e.g., Gusto
# API, Symmetry Tax Engine). Using flat percentages as implementation stubs.
_FICA_RATE = Decimal("0.062")       # 6.2% Social Security
_MEDICARE_RATE = Decimal("0.0145")  # 1.45% Medicare
_FEDERAL_TAX_STUB = Decimal("0.22") # 22% flat (stub — real tables use brackets)
_STATE_TAX_STUB = Decimal("0.05")   # 5% flat state income tax (stub)


class PayrollCalculationService:
    """Calculate gross pay, taxes, and deductions for a PayrollRun."""

    @staticmethod
    def calculate_entry(employee, regular_hours, overtime_hours=0, double_time_hours=0):
        """Return a dict with computed payroll figures for one employee.

        Parameters
        ----------
        employee : Employee
        regular_hours : Decimal
        overtime_hours : Decimal
        double_time_hours : Decimal
        """
        from .models import Employee

        regular_hours = Decimal(str(regular_hours))
        overtime_hours = Decimal(str(overtime_hours))
        double_time_hours = Decimal(str(double_time_hours))

        base_rate = employee.base_hourly_rate
        ot_rate = base_rate * employee.overtime_rate_multiplier
        dt_rate = base_rate * Decimal("2.0")

        gross_pay = (
            regular_hours * base_rate
            + overtime_hours * ot_rate
            + double_time_hours * dt_rate
        ).quantize(Decimal("0.01"))

        fica = (gross_pay * _FICA_RATE).quantize(Decimal("0.01"))
        medicare = (gross_pay * _MEDICARE_RATE).quantize(Decimal("0.01"))
        federal_tax = (gross_pay * _FEDERAL_TAX_STUB).quantize(Decimal("0.01"))
        state_tax = (gross_pay * _STATE_TAX_STUB).quantize(Decimal("0.01"))
        total_tax = fica + medicare + federal_tax + state_tax
        net_pay = (gross_pay - total_tax).quantize(Decimal("0.01"))

        return {
            "regular_hours": regular_hours,
            "overtime_hours": overtime_hours,
            "double_time_hours": double_time_hours,
            "regular_rate": base_rate,
            "gross_pay": gross_pay,
            "federal_tax": federal_tax,
            "state_tax": state_tax,
            "fica": fica,
            "medicare": medicare,
            "deductions": [],
            "net_pay": net_pay,
        }

    @staticmethod
    def calculate_from_time_entries(payroll_run, employees=None):
        """Populate PayrollEntries from field_ops.TimeEntry records.

        Creates or updates one PayrollEntry per employee covering the pay period.
        Returns list of created/updated PayrollEntry instances.
        """
        from apps.field_ops.models import TimeEntry

        from .models import Employee, PayrollEntry

        org = payroll_run.organization
        if employees is None:
            employees = Employee.objects.filter(organization=org, is_active=True)

        entries_created = []
        with transaction.atomic():
            for employee in employees:
                if not employee.user_id:
                    continue  # No app user — cannot correlate time entries

                time_qs = TimeEntry.objects.filter(
                    organization=org,
                    user=employee.user,
                    clock_in__date__gte=payroll_run.pay_period_start,
                    clock_in__date__lte=payroll_run.pay_period_end,
                    status="approved",
                )

                regular_hours = Decimal("0")
                overtime_hours = Decimal("0")
                allocations = []

                for te in time_qs:
                    reg = te.hours - (te.overtime_hours or Decimal("0"))
                    regular_hours += max(reg, Decimal("0"))
                    overtime_hours += te.overtime_hours or Decimal("0")

                    if te.project_id:
                        allocation = {
                            "project_id": str(te.project_id),
                            "cost_code_id": str(te.cost_code_id) if te.cost_code_id else None,
                            "hours": float(te.hours),
                            "amount": float(
                                te.hours * employee.burdened_rate
                            ),
                        }
                        allocations.append(allocation)

                calc = PayrollCalculationService.calculate_entry(
                    employee, regular_hours, overtime_hours
                )
                calc["job_cost_allocations"] = allocations

                entry, _ = PayrollEntry.objects.update_or_create(
                    payroll_run=payroll_run,
                    employee=employee,
                    defaults=calc,
                )
                entries_created.append(entry)

        # Update payroll run totals
        PayrollCalculationService._update_run_totals(payroll_run)
        return entries_created

    @staticmethod
    def _update_run_totals(payroll_run):
        """Recalculate and save aggregate totals on the PayrollRun."""
        from .models import PayrollEntry
        from django.db.models import Sum

        entries = PayrollEntry.objects.filter(payroll_run=payroll_run)
        totals = entries.aggregate(
            gross=Sum("gross_pay"),
            fed=Sum("federal_tax"),
            state=Sum("state_tax"),
            fica=Sum("fica"),
            medicare=Sum("medicare"),
            net=Sum("net_pay"),
        )

        total_taxes = Decimal("0")
        for key in ("fed", "state", "fica", "medicare"):
            total_taxes += totals.get(key) or Decimal("0")

        payroll_run.total_gross = totals.get("gross") or Decimal("0")
        payroll_run.total_taxes = total_taxes
        payroll_run.total_deductions = Decimal("0")  # custom deductions not summed here
        payroll_run.total_net = totals.get("net") or Decimal("0")
        payroll_run.save(
            update_fields=["total_gross", "total_taxes", "total_deductions", "total_net", "updated_at"]
        )

    @staticmethod
    def approve_run(payroll_run, approver):
        """Advance a DRAFT or PROCESSING run to APPROVED."""
        from .models import PayrollRun

        if payroll_run.status not in (PayrollRun.Status.DRAFT, PayrollRun.Status.PROCESSING):
            raise ValueError(
                f"Cannot approve a payroll run with status '{payroll_run.status}'."
            )
        payroll_run.status = PayrollRun.Status.APPROVED
        payroll_run.approved_by = approver
        payroll_run.approved_at = django_tz.now()
        payroll_run.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        return payroll_run

    @staticmethod
    def mark_paid(payroll_run):
        """Mark an APPROVED run as PAID."""
        from .models import PayrollRun

        if payroll_run.status != PayrollRun.Status.APPROVED:
            raise ValueError("Only APPROVED payroll runs can be marked as PAID.")
        payroll_run.status = PayrollRun.Status.PAID
        payroll_run.save(update_fields=["status", "updated_at"])
        return payroll_run

    @staticmethod
    def void_run(payroll_run):
        """Void a payroll run (cannot void a PAID run)."""
        from .models import PayrollRun

        if payroll_run.status == PayrollRun.Status.PAID:
            raise ValueError("Cannot void a PAID payroll run. Contact accounting.")
        payroll_run.status = PayrollRun.Status.VOID
        payroll_run.save(update_fields=["status", "updated_at"])
        return payroll_run


class CertifiedPayrollService:
    """Generate WH-347 certified payroll reports and validate prevailing wages."""

    @staticmethod
    def generate_report(payroll_run, project, report_type="wh_347"):
        """Create a CertifiedPayrollReport and populate compliance issues.

        Returns the CertifiedPayrollReport instance.
        """
        from .models import CertifiedPayrollReport, PayrollEntry, PrevailingWageRate

        org = payroll_run.organization

        # Get entries for employees who worked on this project
        entries = PayrollEntry.objects.filter(payroll_run=payroll_run).select_related("employee")

        # Prevailing wage rates for this project (use most recent per trade)
        wage_rates = {}
        for pwr in PrevailingWageRate.objects.filter(
            organization=org,
            project=project,
            effective_date__lte=payroll_run.pay_period_end,
        ).order_by("-effective_date"):
            if pwr.trade not in wage_rates:
                wage_rates[pwr.trade] = pwr.total_rate

        compliance_issues = []
        for entry in entries:
            project_hours = sum(
                a.get("hours", 0)
                for a in (entry.job_cost_allocations or [])
                if str(a.get("project_id", "")) == str(project.pk)
            )
            if not project_hours:
                continue

            trade = entry.employee.trade
            required_rate = wage_rates.get(trade)
            if required_rate and project_hours:
                paid_rate = entry.regular_rate
                if paid_rate < required_rate:
                    shortfall = (required_rate - paid_rate) * Decimal(str(project_hours))
                    compliance_issues.append({
                        "employee_id": str(entry.employee.pk),
                        "employee_name": entry.employee.full_name,
                        "trade": trade,
                        "hours_on_project": project_hours,
                        "paid_rate": float(paid_rate),
                        "required_rate": float(required_rate),
                        "shortfall": float(shortfall.quantize(Decimal("0.01"))),
                    })

        report, _ = CertifiedPayrollReport.objects.update_or_create(
            organization=org,
            project=project,
            payroll_run=payroll_run,
            defaults={
                "report_type": report_type,
                "week_ending": payroll_run.pay_period_end,
                "status": CertifiedPayrollReport.ReportStatus.DRAFT,
                "compliance_issues": compliance_issues,
            },
        )
        return report

    @staticmethod
    def validate_prevailing_wage(project, payroll_run):
        """Return list of compliance issues for prevailing wage validation.

        Re-uses generate_report logic but returns just the issues list.
        """
        report = CertifiedPayrollService.generate_report(payroll_run, project)
        return report.compliance_issues

    @staticmethod
    def submit_report(report):
        """Mark a certified payroll report as SUBMITTED."""
        from .models import CertifiedPayrollReport

        if report.status != CertifiedPayrollReport.ReportStatus.DRAFT:
            raise ValueError("Only DRAFT reports can be submitted.")
        report.status = CertifiedPayrollReport.ReportStatus.SUBMITTED
        report.save(update_fields=["status", "updated_at"])
        return report


class WorkforceService:
    """Employee certification tracking, expiry alerts, and skills inventory."""

    @staticmethod
    def get_expiring_certifications(organization, days_ahead=30):
        """Return list of {employee, cert_name, expiry} expiring within days_ahead."""
        from .models import Employee

        employees = Employee.objects.filter(organization=organization, is_active=True)
        threshold = date.today() + timedelta(days=days_ahead)
        expiring = []

        for emp in employees:
            for cert in (emp.certifications or []):
                expiry_str = cert.get("expiry")
                if not expiry_str:
                    continue
                try:
                    expiry = date.fromisoformat(expiry_str)
                    if date.today() <= expiry <= threshold:
                        expiring.append({
                            "employee_id": str(emp.pk),
                            "employee_name": emp.full_name,
                            "cert_name": cert.get("name", "Unknown"),
                            "cert_number": cert.get("number", ""),
                            "expiry": expiry_str,
                            "days_until_expiry": (expiry - date.today()).days,
                        })
                except ValueError:
                    logger.warning(
                        "Invalid expiry date '%s' for employee %s", expiry_str, emp.pk
                    )

        expiring.sort(key=lambda x: x["days_until_expiry"])
        return expiring

    @staticmethod
    def get_skills_inventory(organization):
        """Return skills/trade breakdown for active employees."""
        from .models import Employee

        employees = Employee.objects.filter(organization=organization, is_active=True)
        by_trade = {}
        by_type = {}
        total = 0

        for emp in employees:
            total += 1
            by_trade[emp.trade] = by_trade.get(emp.trade, 0) + 1
            by_type[emp.employment_type] = by_type.get(emp.employment_type, 0) + 1

        return {
            "total_active": total,
            "by_trade": by_trade,
            "by_employment_type": by_type,
        }

    @staticmethod
    def update_certification(employee, cert_name, cert_number, expiry, issuing_body=""):
        """Add or update a certification on an employee record."""
        certifications = list(employee.certifications or [])

        # Find existing by name
        for cert in certifications:
            if cert.get("name") == cert_name:
                cert["number"] = cert_number
                cert["expiry"] = str(expiry)
                cert["issuing_body"] = issuing_body
                break
        else:
            certifications.append({
                "name": cert_name,
                "number": cert_number,
                "expiry": str(expiry),
                "issuing_body": issuing_body,
            })

        employee.certifications = certifications
        employee.save(update_fields=["certifications", "updated_at"])
        return employee

    @staticmethod
    def terminate_employee(employee, termination_date=None):
        """Mark an employee as inactive with a termination date."""
        if termination_date is None:
            termination_date = date.today()
        employee.is_active = False
        employee.termination_date = termination_date
        employee.save(update_fields=["is_active", "termination_date", "updated_at"])
        return employee
