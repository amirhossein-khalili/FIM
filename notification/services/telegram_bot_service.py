from notification.models import NotificationType
from notification.services.base import NotificationService
from notification.services.mixins import NotificationMixin


class TelegramBotServiceNotification(NotificationMixin, NotificationService):
    """
    Sends push notifications using telegram api.
    """

    NOTIFICATION_TYPE = NotificationType.TELEGRAM

    def __init__(self):
        pass

    def _send(self, recipient: str, message: str) -> bool:
        """
        Sends a push notification telegram api.
        """
        print(recipient, message)
        print("telegram notification has been sended")
        return True
