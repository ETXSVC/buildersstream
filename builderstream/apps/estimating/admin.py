"""
Django admin configuration for the estimating app.

Registers all 9 models with appropriate inlines, filters, and search fields.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Assembly,
    AssemblyItem,
    CostCode,
    CostItem,
    Estimate,
    EstimateLineItem,
    EstimateSection,
    Proposal,
    ProposalTemplate,
)


# ---------------------------------------------------------------------------
# CostCode
# ---------------------------------------------------------------------------

@admin.register(CostCode)
class CostCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'division', 'category', 'is_labor', 'is_active', 'organization']
    list_filter = ['division', 'is_labor', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['division', 'code']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('organization', 'code', 'name', 'division', 'category'),
        }),
        ('Flags', {
            'fields': ('is_labor', 'is_active'),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ---------------------------------------------------------------------------
# CostItem
# ---------------------------------------------------------------------------

@admin.register(CostItem)
class CostItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'cost_code', 'unit', 'cost', 'base_price',
        'client_price', 'markup_percent', 'is_active', 'organization',
    ]
    list_filter = ['is_active', 'cost_code__division', 'is_taxable']
    search_fields = ['name', 'description', 'cost_code__code', 'cost_code__name']
    ordering = ['name']
    readonly_fields = ['id', 'markup_percent', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('organization', 'cost_code', 'name', 'description', 'unit'),
        }),
        ('Pricing', {
            'fields': ('cost', 'base_price', 'client_price', 'markup_percent', 'labor_hours'),
        }),
        ('Flags', {
            'fields': ('is_taxable', 'is_active'),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ---------------------------------------------------------------------------
# Assembly + AssemblyItem inline
# ---------------------------------------------------------------------------

class AssemblyItemInline(admin.TabularInline):
    model = AssemblyItem
    extra = 0
    fields = ['cost_item', 'quantity', 'sort_order', 'notes']
    readonly_fields = ['id']
    ordering = ['sort_order']


@admin.register(Assembly)
class AssemblyAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_cost', 'total_price', 'is_active', 'organization']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['id', 'total_cost', 'total_price', 'created_at', 'updated_at']
    inlines = [AssemblyItemInline]
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'description'),
        }),
        ('Computed Totals', {
            'fields': ('total_cost', 'total_price'),
        }),
        ('Flags', {
            'fields': ('is_active',),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(AssemblyItem)
class AssemblyItemAdmin(admin.ModelAdmin):
    list_display = ['assembly', 'cost_item', 'quantity', 'sort_order']
    list_filter = ['assembly__organization']
    search_fields = ['assembly__name', 'cost_item__name']
    ordering = ['assembly', 'sort_order']
    readonly_fields = ['id', 'created_at', 'updated_at']


# ---------------------------------------------------------------------------
# Estimate + EstimateSection + EstimateLineItem inlines
# ---------------------------------------------------------------------------

class EstimateLineItemInline(admin.TabularInline):
    model = EstimateLineItem
    extra = 0
    fields = [
        'description', 'quantity', 'unit', 'unit_cost', 'unit_price',
        'line_total', 'cost_item', 'assembly', 'sort_order',
    ]
    readonly_fields = ['id', 'line_total']
    ordering = ['sort_order']


class EstimateSectionInline(admin.TabularInline):
    model = EstimateSection
    extra = 0
    fields = ['name', 'description', 'subtotal', 'sort_order']
    readonly_fields = ['id', 'subtotal']
    ordering = ['sort_order']


@admin.register(EstimateSection)
class EstimateSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'estimate', 'subtotal', 'sort_order']
    list_filter = ['estimate__status', 'estimate__organization']
    search_fields = ['name', 'estimate__name', 'estimate__estimate_number']
    ordering = ['estimate', 'sort_order']
    readonly_fields = ['id', 'subtotal', 'created_at', 'updated_at']
    inlines = [EstimateLineItemInline]


@admin.register(EstimateLineItem)
class EstimateLineItemAdmin(admin.ModelAdmin):
    list_display = [
        'description', 'section', 'quantity', 'unit', 'unit_cost',
        'unit_price', 'line_total', 'sort_order',
    ]
    list_filter = ['section__estimate__status', 'section__estimate__organization']
    search_fields = ['description', 'section__name', 'section__estimate__estimate_number']
    ordering = ['section', 'sort_order']
    readonly_fields = ['id', 'line_total', 'created_at', 'updated_at']


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = [
        'estimate_number', 'name', 'status', 'subtotal', 'tax_amount',
        'total', 'created_by', 'organization',
    ]
    list_filter = ['status', 'organization']
    search_fields = ['estimate_number', 'name', 'created_by__email']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'estimate_number', 'subtotal', 'tax_amount', 'total',
        'approved_at', 'created_at', 'updated_at',
    ]
    inlines = [EstimateSectionInline]
    fieldsets = (
        (None, {
            'fields': (
                'organization', 'estimate_number', 'name', 'project', 'lead',
                'created_by', 'status',
            ),
        }),
        ('Financial', {
            'fields': ('tax_rate', 'subtotal', 'tax_amount', 'total', 'valid_until'),
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at'),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ---------------------------------------------------------------------------
# Proposal
# ---------------------------------------------------------------------------

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = [
        'proposal_number', 'estimate', 'status', 'client',
        'sent_to_email', 'valid_until', 'view_count', 'is_signed', 'organization',
    ]
    list_filter = ['status', 'is_signed', 'organization']
    search_fields = [
        'proposal_number', 'sent_to_email',
        'estimate__estimate_number', 'estimate__name',
        'client__first_name', 'client__last_name',
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'id', 'proposal_number', 'public_token', 'view_count',
        'viewed_at', 'sent_at', 'signed_at', 'is_signed', 'created_at', 'updated_at',
    ]

    def public_link(self, obj):
        if obj.public_token:
            url = f"/api/v1/estimating/public/proposals/{obj.public_token}/"
            return format_html('<a href="{}" target="_blank">View Public</a>', url)
        return '-'
    public_link.short_description = 'Public Link'

    fieldsets = (
        (None, {
            'fields': (
                'organization', 'estimate', 'project', 'lead', 'client',
                'template', 'proposal_number', 'status',
            ),
        }),
        ('Delivery', {
            'fields': ('sent_to_email', 'sent_at', 'valid_until'),
        }),
        ('Tracking', {
            'fields': ('public_token', 'view_count', 'viewed_at'),
        }),
        ('E-Signature', {
            'fields': (
                'is_signed', 'signed_by_name', 'signature_ip',
                'signature_user_agent', 'signed_at', 'signature_image',
            ),
            'classes': ('collapse',),
        }),
        ('Content', {
            'fields': ('terms_and_conditions', 'notes'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ---------------------------------------------------------------------------
# ProposalTemplate
# ---------------------------------------------------------------------------

@admin.register(ProposalTemplate)
class ProposalTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'organization']
    list_filter = ['is_default', 'organization']
    search_fields = ['name']
    ordering = ['-is_default', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'is_default'),
        }),
        ('Template Content', {
            'fields': ('header_text', 'footer_text', 'terms_and_conditions', 'signature_instructions'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
