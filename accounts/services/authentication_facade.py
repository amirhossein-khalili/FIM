from accounts.models import User
from accounts.services.jwt_service_impl import JWTServiceImpl
from accounts.services.otp_service_impl import OTPServiceImpl
from accounts.services.user_validation_impl import UserValidationServiceImpl


class AuthenticationFacade:
    def __init__(self):
        self.otp_service = OTPServiceImpl()
        self.jwt_service = JWTServiceImpl()
        self.user_validation = UserValidationServiceImpl()

    def request_otp(self, phone: str) -> dict:
        return self.otp_service.send_otp(phone)

    def verify_otp_and_authenticate(self, phone: str, otp: str) -> dict:
        if self.otp_service.verify_otp(phone, otp):

            if self.user_validation.user_exists(phone):
                user = User.objects.get(phone=phone)
            else:
                user = User.objects.create_user(phone=phone)

            if self.user_validation.has_user_access(user):
                tokens = self.jwt_service.generate_token(user)

                return {
                    "tokens": tokens,
                    "is_new_user": not self.user_validation.user_exists(phone),
                }

            raise PermissionError("User has no access ")

        raise ValueError("Invalid OTP")
