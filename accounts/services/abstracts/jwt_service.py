from abc import ABC, abstractmethod


class AbstractJWTService(ABC):
    @abstractmethod
    def generate_token(self, user) -> str:
        """
        Generate a JWT token for the given user.
        """
        pass

    @abstractmethod
    def verify_token(self, token: str):
        """
        Verify the JWT token and return the associated user or claims.
        """
        pass
