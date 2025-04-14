from abc import ABC, abstractmethod

from notification.services.base import NotificationService


class NotificationFactory(ABC):
    """
    Abstract Factory for creating notification services.
    """

    @abstractmethod
    def create_notification_service(self) -> NotificationService:
        """
        Creates and returns an instance of a concrete NotificationService.

        :return: An instance of NotificationService (Email, SMS, Push).
        """
        pass
