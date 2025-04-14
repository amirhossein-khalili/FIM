from abc import ABC, abstractmethod


class AbstractOTPService(ABC):
    @abstractmethod
    def send_otp(self, phone: str) -> dict:
        """
        Generate and send an OTP to the given phone number.
        Returns a dict with details like a message or OTP identifier.
        """
        pass

    @abstractmethod
    def verify_otp(self, phone: str, otp: str) -> bool:
        """
        Verify the provided OTP for the given phone number.
        Returns True if verification succeeds, otherwise False.
        """
        pass
