"""Management command to create a demo organization with sample data."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tenants.models import ActiveModule, Organization, OrganizationMembership

User = get_user_model()


class Command(BaseCommand):
    help = "Create a demo organization with sample users and modules."

    def add_arguments(self, parser):
        parser.add_argument(
            "--owner-email",
            type=str,
            default="admin@builderstream.com",
            help="Email for the organization owner (default: admin@builderstream.com)",
        )
        parser.add_argument(
            "--org-name",
            type=str,
            default="Demo Construction Co.",
            help="Organization name (default: Demo Construction Co.)",
        )
        parser.add_argument(
            "--no-sample-users",
            action="store_true",
            help="Skip creating sample team members.",
        )

    def handle(self, *args, **options):
        owner_email = options["owner_email"]
        org_name = options["org_name"]

        # 1. Create or get the owner user
        owner, created = User.objects.get_or_create(
            email=owner_email,
            defaults={
                "first_name": "Demo",
                "last_name": "Owner",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            owner.set_password("demo1234!")
            owner.save()
            self.stdout.write(self.style.SUCCESS(f"Created owner user: {owner_email}"))
        else:
            self.stdout.write(f"Owner user already exists: {owner_email}")

        # 2. Create the organization
        org, created = Organization.objects.get_or_create(
            slug="demo-construction",
            defaults={
                "name": org_name,
                "owner": owner,
                "email": owner_email,
                "phone": "+1-555-0100",
                "industry_type": Organization.IndustryType.COMMERCIAL_GC,
                "subscription_plan": Organization.SubscriptionPlan.PROFESSIONAL,
                "subscription_status": Organization.SubscriptionStatus.TRIALING,
                "trial_ends_at": timezone.now() + timezone.timedelta(days=14),
                "max_users": 25,
                "address_line1": "123 Construction Ave",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78701",
                "country": "US",
                "settings": {
                    "default_currency": "USD",
                    "timezone": "America/Chicago",
                    "fiscal_year_start": "01",
                },
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created organization: {org_name}"))
        else:
            self.stdout.write(f"Organization already exists: {org_name}")
            return

        # 3. Create OWNER membership
        OrganizationMembership.objects.get_or_create(
            user=owner,
            organization=org,
            defaults={
                "role": OrganizationMembership.Role.OWNER,
                "is_active": True,
                "accepted_at": timezone.now(),
            },
        )

        # 4. Activate all modules for demo
        for module_key, _ in ActiveModule.ModuleKey.choices:
            ActiveModule.objects.get_or_create(
                organization=org,
                module_key=module_key,
                defaults={"is_active": True},
            )
        self.stdout.write(self.style.SUCCESS("Activated all modules"))

        # 5. Create sample team members
        if not options["no_sample_users"]:
            sample_members = [
                ("pm@builderstream.com", "Pat", "Manager", OrganizationMembership.Role.PROJECT_MANAGER),
                ("estimator@builderstream.com", "Ed", "Estimator", OrganizationMembership.Role.ESTIMATOR),
                ("field@builderstream.com", "Frank", "Field", OrganizationMembership.Role.FIELD_WORKER),
                ("accountant@builderstream.com", "Alice", "Accountant", OrganizationMembership.Role.ACCOUNTANT),
                ("readonly@builderstream.com", "Rick", "Readonly", OrganizationMembership.Role.READ_ONLY),
            ]

            for email, first, last, role in sample_members:
                user, _ = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "first_name": first,
                        "last_name": last,
                    },
                )
                user.set_password("demo1234!")
                user.save()

                OrganizationMembership.objects.get_or_create(
                    user=user,
                    organization=org,
                    defaults={
                        "role": role,
                        "is_active": True,
                        "invited_by": owner,
                        "invited_at": timezone.now(),
                        "accepted_at": timezone.now(),
                    },
                )
                self.stdout.write(f"  Created {role} member: {email}")

        # 6. Set owner's last active organization
        owner.last_active_organization = org
        owner.save(update_fields=["last_active_organization"])

        self.stdout.write(self.style.SUCCESS(
            f"\nDemo organization '{org_name}' created successfully!\n"
            f"  Owner: {owner_email} / demo1234!\n"
            f"  Members: {org.memberships.count()} total\n"
            f"  Modules: {org.active_modules.count()} active"
        ))
