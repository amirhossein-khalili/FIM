from django.apps import AppConfig


class NotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    name = "notification"

    def ready(self):
        from .models import NotificationType
        from .provider import notification_service_creator
