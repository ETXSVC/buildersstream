"""Estimating admin configuration."""
from django.contrib import admin

from .models import CostCode, Estimate, EstimateLineItem


@admin.register(CostCode)
class CostCodeAdmin(admin.ModelAdmin):
    list_display = ["code", "description", "unit", "unit_cost", "category"]
    list_filter = ["category"]
    search_fields = ["code", "description"]


class EstimateLineItemInline(admin.TabularInline):
    model = EstimateLineItem
    extra = 0


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "status", "markup_percentage"]
    list_filter = ["status"]
    inlines = [EstimateLineItemInline]
