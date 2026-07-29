from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Notifications'

    def ready(self):
        # Registers the Order post_save/pre_save listeners that fire
        # purchase / delivery notifications automatically.
        import notifications.signals  # noqa: F401
