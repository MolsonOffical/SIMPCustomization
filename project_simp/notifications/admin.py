from django.contrib import admin, messages

from .models import BroadcastMessage, Notification
from .services import send_admin_broadcast


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'read_at')


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'sent_by', 'recipient_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'message')
    readonly_fields = ('sent_by', 'recipient_count', 'created_at')

    def get_fields(self, request, obj=None):
        if obj is None:
            return ('title', 'message')
        return ('title', 'message', 'sent_by', 'recipient_count', 'created_at')

    def has_change_permission(self, request, obj=None):
        return obj is None

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        recipient_count = send_admin_broadcast(obj.title, obj.message)
        obj.sent_by = request.user
        obj.recipient_count = recipient_count
        super().save_model(request, obj, form, change)
        messages.success(request, f'Broadcast sent to {recipient_count} users.')