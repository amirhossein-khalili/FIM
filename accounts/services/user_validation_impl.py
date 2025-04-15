from accounts.models import User
from accounts.services.abstracts.user_validation_service import (
    AbstractUserValidationService,
)


class UserValidationServiceImpl(AbstractUserValidationService):
    def user_exists(self, user_name: str) -> bool:
        return User.objects.filter(user_name=user_name).exists()

    def has_user_access(self, user) -> bool:
        return user.is_active and user.is_approved
