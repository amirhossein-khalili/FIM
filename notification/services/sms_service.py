from typing import Dict, List

from notification.models import NotificationType
from notification.services.base import NotificationService
from notification.services.sms_providers.base_sms_provider import BaseSMSProvider

from .mixins import NotificationMixin


class SMSNotificationService(NotificationMixin, NotificationService):
    """
    Concrete implementation of NotificationService for sending SMS using a provider.
    """

    NOTIFICATION_TYPE = NotificationType.SMS

    def __init__(self, sms_provider: BaseSMSProvider):
        """
        Initialize the SMS service with a provider.

        :param sms_provider: An instance of a class that implements BaseSMSProvider.
        """
        self.sms_provider = sms_provider

    def _send(self, recipient: str, message: str) -> bool:
        """
        Sends an SMS using the configured provider.
        """
        return self.sms_provider.send_sms(recipient, message)
