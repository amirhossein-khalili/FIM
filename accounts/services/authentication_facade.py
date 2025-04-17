from django.core.exceptions import ValidationError

from accounts.models import User
from accounts.services.jwt_service_impl import JWTServiceImpl
from accounts.services.signup_alert_service_impl import AdminAlertService
from accounts.services.user_validation_impl import UserValidationServiceImpl


class AuthenticationFacade:
    def __init__(self):
        self.jwt_service = JWTServiceImpl()
        self.user_validation = UserValidationServiceImpl()
        self.telegram_service = AdminAlertService()

    def signup(self, username: str, password: str) -> dict:


        # Create the user with the username and password
        user = User.objects.create_user(user_name=username, password=password)
        
        # Send notification to Telegram bot about new signup
        self.telegram_service.send_signup_notification(user)
        
        return {"message": "Signup successful. Awaiting admin approval."}

    def approve_user(self, user_id: int) -> dict:
        try:
            user = User.objects.get(id=user_id)
            user.is_approved = True
            user.save()
            return {"message": "User approved successfully."}
        except User.DoesNotExist:
            return {"error": "User not found."}

    def login(self, username: str, password: str) -> dict:
        user = User.objects.get(user_name=username)

        # Check if user is approved
        if user.is_approved:
            if user.check_password(password):
                tokens = self.jwt_service.generate_token(user)
                return {"tokens": tokens}
            else:
                return {"error": "Invalid password"}
        else:
            return {"error": "User not approved by admin"}
