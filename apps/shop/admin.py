"""Django admin registration for the shop models."""

from django.contrib import admin

from . import models


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    readonly_fields = ('line_total',)


class PaymentInline(admin.TabularInline):
    model = models.Payment
    extra = 0


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'status')
    list_filter = ('status',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ProductReviewInline(admin.TabularInline):
    model = models.ProductReview
    extra = 0
    fields = ('user', 'rating', 'comment', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user',)


class ProductFileInline(admin.TabularInline):
    model = models.ProductFile
    extra = 0
    fields = ('file', 'title', 'original_name', 'size', 'order')
    readonly_fields = ('size',)


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 0


class EducatorRateInline(admin.TabularInline):
    model = models.EducatorRate
    extra = 0


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'fulfilment', 'category', 'price', 'discount_percent', 'educator',
                    'rating', 'featured', 'status', 'created_at')
    list_filter = ('fulfilment', 'status', 'level', 'featured', 'category', 'created_at')
    search_fields = ('name', 'sku', 'description', 'summary')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [ProductFileInline, ProductImageInline, ProductVariantInline, EducatorRateInline, ProductReviewInline]


@admin.register(models.DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'product', 'file', 'ip_address')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'product__name')
    readonly_fields = ('created_at', 'user', 'product', 'file', 'ip_address')


@admin.register(models.ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'user__email', 'comment')
    autocomplete_fields = ('product', 'user')


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'buyer', 'status', 'total', 'discount_total', 'coupon', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_no', 'buyer__email', 'buyer__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    autocomplete_fields = ('buyer',)
    inlines = [OrderItemInline, PaymentInline]


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'line_total', 'expiry_date')
    list_filter = ('expiry_date',)
    search_fields = ('order__order_no', 'product__name')


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'paid_at')
    list_filter = ('status', 'method', 'paid_at')
    search_fields = ('order__order_no', 'reference')
    date_hierarchy = 'paid_at'



@admin.register(models.Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('start', 'product', 'educator', 'student', 'minutes', 'price', 'status')
    list_filter = ('status', 'product', 'start')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'product__name')
    date_hierarchy = 'start'
    raw_id_fields = ('order_item', 'meeting', 'student', 'cancelled_by')


@admin.register(models.EducatorAvailability)
class EducatorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('educator', 'weekday', 'start_time', 'end_time')
    list_filter = ('weekday',)


@admin.register(models.EducatorTimeOff)
class EducatorTimeOffAdmin(admin.ModelAdmin):
    list_display = ('educator', 'start', 'end', 'reason')


@admin.register(models.CreditEntry)
class CreditEntryAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'amount', 'reason')
    search_fields = ('user__email', 'reason')
    raw_id_fields = ('user', 'booking', 'invoice', 'created_by')


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'user', 'city', 'province', 'postal_code', 'is_default')
    search_fields = ('recipient', 'user__email', 'city', 'suburb')
    raw_id_fields = ('user',)


@admin.register(models.Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'method', 'carrier', 'tracking_reference', 'charged', 'updated_at')
    list_filter = ('status', 'method', 'carrier')
    search_fields = ('order__order_no', 'tracking_reference')
    raw_id_fields = ('order', 'booked_by')
