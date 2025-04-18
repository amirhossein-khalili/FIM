from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework_simplejwt.tokens import AccessToken

from accounts.models import User
from accounts.services.authentication_facade import AuthenticationFacade
from accounts.services.jwt_service_impl import JWTServiceImpl
from accounts.services.signup_alert_service_impl import AdminAuthAlertService
from accounts.services.user_validation_impl import UserValidationServiceImpl
from notification.models import NotificationType


class TestAuthenticationFacade(TestCase):
    def setUp(self):
        self.facade = AuthenticationFacade()
        self.username = "testuser"
        self.password = "testpass123"
        self.user = User.objects.create_user(
            user_name=self.username, password=self.password, is_approved=False
        )

    @patch.object(UserValidationServiceImpl, "user_exists")
    def test_signup_success(self, mock_user_exists):
        import time

        unique_username = f"testuser_{int(time.time())}"  # e.g., testuser_1744905414
        mock_user_exists.return_value = False
        with patch.object(
            self.facade.telegram_service, "send_signup_notification"
        ) as mock_notification:
            result = self.facade.signup(unique_username, self.password)
            self.assertEqual(
                result, {"message": "Signup successful. Awaiting admin approval."}
            )
            mock_notification.assert_called_once()
            user = User.objects.get(user_name=unique_username)
            self.assertFalse(user.is_approved)

    def test_approve_user_success(self):
        result = self.facade.approve_user(self.user.id)
        self.assertEqual(result, {"message": "User approved successfully."})
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.is_approved)

    def test_approve_user_not_found(self):
        result = self.facade.approve_user(999)
        self.assertEqual(result, {"error": "User not found."})

    def test_login_success(self):
        self.user.is_approved = True
        self.user.save()
        with patch.object(
            self.facade.jwt_service, "generate_token"
        ) as mock_generate_token:
            mock_generate_token.return_value = {
                "access": "fake_access",
                "refresh": "fake_refresh",
            }
            result = self.facade.login(self.username, self.password)
            self.assertEqual(
                result, {"tokens": {"access": "fake_access", "refresh": "fake_refresh"}}
            )
            mock_generate_token.assert_called_once_with(self.user)

    def test_login_invalid_password(self):
        self.user.is_approved = True
        self.user.save()
        result = self.facade.login(self.username, "wrongpass")
        self.assertEqual(result, {"error": "Invalid password"})

    def test_login_user_not_approved(self):
        result = self.facade.login(self.username, self.password)
        self.assertEqual(result, {"error": "User not approved by admin"})

    # def test_login_user_not_found(self):
    #     result = self.facade.login("nonexistent", self.password)
    #     self.assertEqual(result, {"error": "User not found."})


class TestJWTServiceImpl(TestCase):
    def setUp(self):
        self.jwt_service = JWTServiceImpl()
        self.user = User.objects.create_user(
            user_name="testuser", password="testpass123"
        )

    def test_generate_token(self):
        tokens = self.jwt_service.generate_token(self.user)
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)
        access_token = AccessToken(tokens["access"])
        self.assertEqual(access_token["user_id"], self.user.id)
        self.assertEqual(access_token["token_type"], "access")

    @patch(
        "rest_framework_simplejwt.authentication.JWTAuthentication.get_validated_token"
    )
    def test_verify_token_valid(self, mock_get_validated_token):
        mock_get_validated_token.return_value = {"user_id": self.user.id}
        token = "valid_token"
        validated_token = self.jwt_service.verify_token(token)
        self.assertEqual(validated_token, {"user_id": self.user.id})
        mock_get_validated_token.assert_called_once_with(token)

    @patch(
        "rest_framework_simplejwt.authentication.JWTAuthentication.get_validated_token"
    )
    def test_verify_token_invalid(self, mock_get_validated_token):
        mock_get_validated_token.side_effect = Exception("Invalid token")
        with self.assertRaises(Exception) as context:
            self.jwt_service.verify_token("invalid_token")
        self.assertEqual(str(context.exception), "Invalid or expired token")


class TestAdminAlertService(TestCase):
    def setUp(self):
        self.alert_service = AdminAuthAlertService()
        self.user = User.objects.create_user(
            user_name="testuser", password="testpass123"
        )

    @patch("accounts.services.signup_alert_service_impl.notification_service_creator")
    def test_send_signup_notification(self, mock_notification_creator):
        mock_alert_sender = MagicMock()
        mock_notification_creator.return_value = mock_alert_sender
        self.alert_service.send_signup_notification(self.user)
        mock_notification_creator.assert_called_once_with(NotificationType.TELEGRAM)
        mock_alert_sender.send_notification.assert_called_once_with(
            "admin receiver",
            f"some one has been sign up the user information {self.user}",
        )


class TestUserValidationServiceImpl(TestCase):
    def setUp(self):
        self.validation_service = UserValidationServiceImpl()
        self.user = User.objects.create_user(
            user_name="testuser",
            password="testpass123",
            is_active=True,
            is_approved=True,
        )

    def test_user_exists_true(self):
        result = self.validation_service.user_exists("testuser")
        self.assertTrue(result)

    def test_user_exists_false(self):
        result = self.validation_service.user_exists("nonexistent")
        self.assertFalse(result)

    def test_has_user_access_true(self):
        result = self.validation_service.has_user_access(self.user)
        self.assertTrue(result)

    def test_has_user_access_false_not_active(self):
        self.user.is_active = False
        self.user.save()
        result = self.validation_service.has_user_access(self.user)
        self.assertFalse(result)

    def test_has_user_access_false_not_approved(self):
        self.user.is_approved = False
        self.user.save()
        result = self.validation_service.has_user_access(self.user)
        self.assertFalse(result)
