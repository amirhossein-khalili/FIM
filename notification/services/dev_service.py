from datetime import datetime
from typing import Dict, List

from notification.models import NotificationType
from notification.services.base import NotificationService

from .mixins import NotificationMixin


class DevNotificationService(NotificationMixin, NotificationService):
    """
    A development notification service that prints notifications to the terminal.
    This service is used only when DEBUG is True.
    """

    NOTIFICATION_TYPE = NotificationType.DEV

    def _send(self, recipient: str, message: str) -> None:
        """
        Print the notification to the terminal and store it in memory.
        """
        print("=======================")
        print(f"[DEV] Notification to {recipient}")
        print("=======================")
        print(message)
        print("=======================")

        return True
