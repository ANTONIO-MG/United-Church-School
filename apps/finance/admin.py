"""Django admin registration for the finance models."""

from django.contrib import admin

from . import models


class InvoiceItemInline(admin.TabularInline):
    model = models.InvoiceItem
    extra = 0
    readonly_fields = ('amount',)


class InvoicePaymentInline(admin.TabularInline):
    model = models.InvoicePayment
    extra = 0


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'status', 'total', 'issue_date', 'due_date')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('number', 'customer__email', 'customer__username')
    date_hierarchy = 'issue_date'
    ordering = ('-issue_date',)
    autocomplete_fields = ('customer',)
    inlines = [InvoiceItemInline, InvoicePaymentInline]


@admin.register(models.InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'amount')
    search_fields = ('description', 'invoice__number')


@admin.register(models.InvoicePayment)
class InvoicePaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'method', 'gateway', 'status', 'paid_at')
    list_filter = ('status', 'gateway', 'method', 'paid_at')
    search_fields = ('invoice__number', 'reference', 'gateway_ref')
    date_hierarchy = 'paid_at'


@admin.register(models.ProofOfPayment)
class ProofOfPaymentAdmin(admin.ModelAdmin):
    """Every payment on record. Staff capture EFT slips here or on the
    grant-access page; gateway payments file themselves."""
    list_display = ('person', 'amount', 'source', 'status', 'paid_on', 'granted_months',
                    'reference', 'recorded_by')
    list_filter = ('source', 'status', 'paid_on')
    search_fields = ('person__first_name', 'person__last_name', 'person__user__email',
                     'reference', 'note', 'invoice__number')
    autocomplete_fields = ('person', 'invoice', 'payment')
    readonly_fields = ('created_at', 'updated_at', 'original_name', 'content_type')
    date_hierarchy = 'paid_on'
