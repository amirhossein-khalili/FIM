from accounts.models import User
from accounts.services.abstracts.user_validation_service import (
    AbstractUserValidationService,
)


class UserValidationServiceImpl(AbstractUserValidationService):
    def user_exists(self, phone: str) -> bool:
        """
        Check if a user with the given phone number exists.
        """
        return User.objects.filter(phone=phone).exists()

    def has_user_access(self, user) -> bool:
        return user.is_active
