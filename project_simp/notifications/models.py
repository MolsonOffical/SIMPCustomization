from django.conf import settings
from django.db import models
from django.utils import timezone


class NotificationType(models.TextChoices):
    PURCHASE = 'purchase', 'Purchase'
    DELIVERY = 'delivery', 'Delivery'
    ADMIN = 'admin', 'Admin Broadcast'
    GENERAL = 'general', 'General'
    FAILED = 'failed', 'Failed'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()

    order = models.ForeignKey(
        'shoes.Order',
        on_delete=models.SET_NULL,
        related_name='notifications',
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title} -> {self.user}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])

class BroadcastMessage(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broadcast_messages',
    )
    recipient_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Broadcast'

    def __str__(self):
        return self.title