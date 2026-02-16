"""Tenant admin configuration."""
from django.contrib import admin

from .models import ActiveModule, Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        "name", "slug", "owner", "industry_type",
        "subscription_plan", "subscription_status",
        "max_users", "is_active", "created_at",
    ]
    list_filter = [
        "is_active", "industry_type",
        "subscription_plan", "subscription_status",
    ]
    search_fields = ["name", "slug", "email", "owner__email"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        "stripe_customer_id", "stripe_subscription_id",
        "created_at", "updated_at",
    ]
    fieldsets = (
        (None, {
            "fields": ("name", "slug", "owner", "logo"),
        }),
        ("Contact", {
            "fields": ("phone", "email", "website"),
        }),
        ("Address", {
            "fields": (
                "address_line1", "address_line2",
                "city", "state", "zip_code", "country",
            ),
        }),
        ("Business", {
            "fields": ("industry_type", "settings"),
        }),
        ("Subscription", {
            "fields": (
                "subscription_plan", "subscription_status",
                "trial_ends_at", "max_users",
                "stripe_customer_id", "stripe_subscription_id",
            ),
        }),
        ("Status", {
            "fields": ("is_active", "created_at", "updated_at"),
        }),
    )


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = [
        "user", "organization", "role",
        "is_active", "invited_by", "accepted_at",
    ]
    list_filter = ["role", "is_active"]
    search_fields = [
        "user__email", "user__first_name", "user__last_name",
        "organization__name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["user", "organization", "invited_by"]


@admin.register(ActiveModule)
class ActiveModuleAdmin(admin.ModelAdmin):
    list_display = [
        "organization", "module_key",
        "is_active", "activated_at", "created_at",
    ]
    list_filter = ["module_key", "is_active"]
    search_fields = ["organization__name", "module_key"]
    readonly_fields = ["activated_at", "created_at", "updated_at"]
