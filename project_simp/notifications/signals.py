from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from shoes.models import Order

from .services import notify_delivery_success, notify_order_failed, notify_purchase_success

STATUS_HANDLERS = {
    'paid': notify_purchase_success,
    'delivered': notify_delivery_success,
    'failed': notify_order_failed,
}

@receiver(pre_save, sender=Order)
def cache_previous_order_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = Order.objects.only('status').get(pk=instance.pk).status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):

    if created:
        return

    previous_status = getattr(instance, '_previous_status', None)
    if previous_status == instance.status:
        return

    handler = STATUS_HANDLERS.get(instance.status)
    if handler:
        handler(instance)
