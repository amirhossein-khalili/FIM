from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.services.abstracts.jwt_service import AbstractJWTService


class JWTServiceImpl(AbstractJWTService):
    def generate_token(self, user) -> dict:
        """
        Generate and return a pair of tokens (access and refresh) for the given user.
        Uses DRF Simple JWT's RefreshToken.
        """
        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}

    def verify_token(self, token: str):
        """
        Verify the JWT token.
        Uses DRF Simple JWT's JWTAuthentication to validate the token.
        Returns the validated token (which includes claims) if valid.
        """
        jwt_authenticator = JWTAuthentication()
        try:
            validated_token = jwt_authenticator.get_validated_token(token)
            return validated_token
        except Exception as e:
            raise Exception("Invalid or expired token") from e
