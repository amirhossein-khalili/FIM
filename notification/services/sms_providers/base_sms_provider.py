from abc import ABC, abstractmethod


class BaseSMSProvider(ABC):
    """
    Abstract class for SMS providers.
    Defines the interface for sending SMS messages.
    """

    @abstractmethod
    def send_sms(self, recipient: str, message: str) -> bool:
        """
        Send an SMS message.

        :param recipient: The recipient's phone number.
        :param message: The SMS content.
        :return: True if sent successfully, False otherwise.
        """
        pass
