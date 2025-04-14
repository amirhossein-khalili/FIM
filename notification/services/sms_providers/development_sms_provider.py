from django.conf import settings
from kavenegar import APIException, HTTPException, KavenegarAPI

from notification.services.sms_providers.base_sms_provider import BaseSMSProvider


class DevelopmentSMSProvider(BaseSMSProvider):
    """
    SMS provider using console.
    """

    def send_sms(self, recipient: str, message: str) -> bool:
        print("=======================")
        print(f"[DEV] send sms to {recipient}")
        print("=======================")
        print(message)
        print("=======================")
        return True
