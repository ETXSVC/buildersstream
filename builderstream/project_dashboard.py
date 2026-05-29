import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.tenants.models import Organization
from apps.projects.services import DashboardService

User = get_user_model()

class Command(BaseCommand):
    help = "Displays a basic dashboard for the project command center in the terminal."

    def add_arguments(self, parser):
        parser.add_argument("org_slug", type=str, help="Slug of the organization to view")
        parser.add_argument("email", type=str, help="Email of the user accessing the dashboard")
        parser.add_argument("--json", action="store_true", help="Output raw JSON data")

    def handle(self, *args, **options):
        org_slug = options["org_slug"]
        email = options["email"]
        as_json = options["json"]

        try:
            org = Organization.objects.get(slug=org_slug)
        except Organization.DoesNotExist:
            raise CommandError(f"Organization with slug '{org_slug}' not found.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f"User with email '{email}' not found.")

        # Fetch data using the existing service
        data = DashboardService.get_dashboard_data(org, user)

        if as_json:
            self.stdout.write(json.dumps(data, indent=2, default=str))
            return

        # Render Text Dashboard
        self.stdout.write(self.style.SUCCESS(f"\n=== DASHBOARD: {org.name} ===\n"))

        # 1. Financial Snapshot
        fin = data.get("financial_snapshot", {})
        self.stdout.write(self.style.MIGRATE_HEADING("Financial Snapshot"))
        self.stdout.write(f"  Total Est. Value:   ${fin.get('total_estimated_value', '0')}")
        self.stdout.write(f"  Total Act. Revenue: ${fin.get('total_actual_revenue', '0')}")
        self.stdout.write(f"  Total Est. Cost:    ${fin.get('total_estimated_cost', '0')}")
        self.stdout.write(f"  Total Act. Cost:    ${fin.get('total_actual_cost', '0')}")

        # 2. Active Projects
        proj = data.get("active_projects", {})
        self.stdout.write(self.style.MIGRATE_HEADING(f"\nActive Projects ({proj.get('count', 0)})"))
        dist = proj.get("status_distribution", {})
        if dist:
            for status, count in dist.items():
                self.stdout.write(f"  - {status.replace('_', ' ').title()}: {count}")
        else:
            self.stdout.write("  No active projects.")

        # 3. Schedule Overview
        sched = data.get("schedule_overview", {})
        self.stdout.write(self.style.MIGRATE_HEADING("\nSchedule Health"))
        self.stdout.write(f"  On Track (Green): {sched.get('projects_on_track', 0)}")
        self.stdout.write(f"  At Risk (Yellow): {sched.get('projects_at_risk', 0)}")
        self.stdout.write(f"  Behind (Red):     {sched.get('projects_behind', 0)}")
        self.stdout.write(f"  Overdue:          {sched.get('overdue_projects', 0)}")

        # 4. Top Action Items
        items = data.get("action_items", [])
        self.stdout.write(self.style.MIGRATE_HEADING(f"\nTop Action Items ({len(items)})"))
        if items:
            for item in items[:5]:
                priority = item.get('priority', 'medium').upper()
                title = item.get('title', 'No Title')
                due = item.get('due_date', 'No Date')
                self.stdout.write(f"  [{priority}] {title} (Due: {due})")
        else:
            self.stdout.write("  No pending action items.")

        self.stdout.write("\n")