"""Billing admin configuration."""
from django.contrib import admin

from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_monthly", "max_users", "max_projects", "is_active"]
    list_filter = ["is_active"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["organization", "plan", "status", "current_period_end"]
    list_filter = ["status"]
