from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Shoes, ShoesColor, ShoesSize, ShoesVariant, Review, ReviewMedia, ReviewReply, Order, OrderItem

# Register your models here.
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Shoes)
admin.site.register(ShoesColor)
admin.site.register(ShoesSize)
admin.site.register(ShoesVariant)


class ReviewMediaInline(admin.TabularInline):
    model = ReviewMedia
    extra = 0


class ReviewReplyInline(admin.StackedInline):
    model = ReviewReply
    extra = 0
    max_num = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('shoe', 'user', 'rating', 'is_anonymous', 'created_at')
    list_filter = ('rating', 'is_anonymous')
    search_fields = ('shoe__name', 'user__username', 'comment')
    inlines = [ReviewMediaInline, ReviewReplyInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'price', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'full_name', 'status_badge', 'payment_method',
        'total_amount', 'transaction_id', 'created_at',
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_id', 'full_name', 'phone', 'transaction_id')
    readonly_fields = ('order_id', 'transaction_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    def status_badge(self, obj):
        colors = {
            'pending_payment': '#a15c00',
            'paid': '#1e7a3d',
            'processing': '#2563eb',
            'shipped': '#7c3aed',
            'delivered': '#111111',
            'failed': '#c0392b',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color, obj.get_status_display(),
        )
    status_badge.short_description = 'Status'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'variant', 'price', 'quantity', 'subtotal')
    readonly_fields = ('order', 'variant', 'price', 'quantity')

    def subtotal(self, obj):
        return obj.subtotal()