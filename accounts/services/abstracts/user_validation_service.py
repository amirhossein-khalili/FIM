from abc import ABC, abstractmethod


class AbstractUserValidationService(ABC):
    @abstractmethod
    def user_exists(self, user_name: str) -> bool:
        """
        Check if a user with the given user_name number exists.
        """
        pass

    @abstractmethod
    def has_user_access(self, user) -> bool:
        """
        Check if the user has access to the system (e.g., active, verified, etc.).
        """
        pass
