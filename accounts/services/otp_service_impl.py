import random

from django.utils import timezone

from accounts.models import OTP
from accounts.services.abstracts.otp_service import AbstractOTPService
from notification.models import NotificationType
from notification.provider import notification_service_creator


class OTPServiceImpl(AbstractOTPService):

    def __init__(self, *args, **kwargs):
        self._notification_service = notification_service_creator(NotificationType.DEV)

    def send_otp(self, phone: str) -> dict:
        """
        Generate a 4-digit OTP, store it in the database, and trigger the sending mechanism.
        Note: In production, do not return the OTP code in the response.
        """
        #  generate the otp code
        otp_code = str(random.randint(1000, 9999))
        otp_instance = OTP.objects.create(phone=phone, code=otp_code)

        self._notification_service.send_notification(
            recipient=phone, message=f"you otp code is \n {otp_code}"
        )

        return {
            "message": "OTP sent successfully",
        }

    def verify_otp(self, phone: str, otp: str) -> bool:
        """
        Verify the OTP for the provided phone number. If the OTP is valid,
        mark it as used and return True; otherwise, return False.
        """

        try:
            otp_instance = OTP.objects.get(phone=phone, code=otp, used=False)
            if otp_instance.is_valid():
                otp_instance.used = True
                otp_instance.save()
                return True
            return False
        except OTP.DoesNotExist:
            return False
