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


def _order_item_thumbnail_html(obj):
    """Shared renderer used by both the inline and the standalone
    OrderItem admin. Relies on OrderItem.display_photo_url, which
    returns the customer's actual custom-design snapshot for
    customizer items (OrderItem.photo) or the catalog product photo
    for variant-based items (variant.shoes_photo)."""
    url = obj.display_photo_url
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="height:50px;width:50px;object-fit:cover;border-radius:6px;" />',
        url,
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('thumbnail', 'variant', 'pattern', 'size', 'colors', 'price', 'quantity')
    fields = ('thumbnail', 'variant', 'pattern', 'size', 'colors', 'price', 'quantity')
    can_delete = False

    def thumbnail(self, obj):
        return _order_item_thumbnail_html(obj)
    thumbnail.short_description = "Photo"


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
    actions = ['mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    def status_badge(self, obj):
        colors = {
            'pending_payment': '#a15c00',
            'paid': '#1e7a3d',
            'processing': '#2563eb',
            'shipped': '#7c3aed',
            'delivered': '#111111',
            'cancelled': '#c0392b',
            'failed': '#c0392b',
        }
        color = colors.get(obj.status, '#666')
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            color, obj.get_status_display(),
        )
    status_badge.short_description = 'Status'

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        updated = queryset.exclude(status__in=['cancelled', 'failed']).update(status='processing')
        self.message_user(request, f"{updated} order(s) marked Processing.")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        updated = queryset.exclude(status__in=['cancelled', 'failed']).update(status='shipped')
        self.message_user(request, f"{updated} order(s) marked Shipped.")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        updated = queryset.exclude(status__in=['cancelled', 'failed']).update(status='delivered')
        self.message_user(request, f"{updated} order(s) marked Delivered.")

    @admin.action(description="Cancel selected orders")
    def mark_cancelled(self, request, queryset):
        updated = queryset.exclude(status='delivered').update(status='cancelled')
        self.message_user(request, f"{updated} order(s) cancelled.")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'thumbnail', 'item_name', 'price', 'quantity', 'subtotal')
    readonly_fields = ('order', 'variant', 'price', 'quantity', 'thumbnail')

    def thumbnail(self, obj):
        return _order_item_thumbnail_html(obj)
    thumbnail.short_description = "Photo"

    def item_name(self, obj):
        if obj.variant_id:
            return str(obj.variant)
        return f"{obj.pattern} (size {obj.size})"
    item_name.short_description = "Item"

    def subtotal(self, obj):
        return obj.subtotal()