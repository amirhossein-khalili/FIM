from abc import ABC, abstractmethod
from typing import Dict, List

from notification.models import Notification


class NotificationService(ABC):
    """
    Abstract class for notification services.
    Defines the interface for sending notifications and retrieving sent notifications.
    """

    NOTIFICATION_TYPE = None

    @abstractmethod
    def _send(self, recipient: str, message: str) -> bool:
        """
        Subclasses must implement this to actually send a notification.
        Should return True if successful, False otherwise.
        """
        pass

    def send_notification(self, recipient: str, message: str) -> None:
        """
        Send a notification and store the result.
        """
        if not self.NOTIFICATION_TYPE:
            raise ValueError("NOTIFICATION_TYPE must be defined in the subclass.")

        success = self._send(recipient, message)
        Notification.objects.create(
            recipient=recipient,
            message=message,
            notification_type=self.NOTIFICATION_TYPE,
            status=success,
        )

    @abstractmethod
    def list_notifications(self) -> List[Dict[str, str]]:
        """
        Retrieve a list of sent notifications.

        :return: A list of dictionaries containing notification details (e.g., recipient, message, timestamp).
        """
        pass
