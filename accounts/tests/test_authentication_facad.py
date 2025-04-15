# from unittest.mock import MagicMock, patch

# from django.test import TestCase

# from accounts.services.authentication_facade import AuthenticationFacade
# from accounts.services.jwt_service_impl import JWTServiceImpl
# from accounts.services.otp_service_impl import OTPServiceImpl
# from accounts.services.user_validation_impl import UserValidationServiceImpl


# class AuthenticationFacadeTest(TestCase):

#     def setUp(self):
#         # Patch the notification_service_creator function manually
#         patcher = patch(
#             "accounts.services.otp_service_impl.notification_service_creator"
#         )
#         self.mock_notification_service_creator = patcher.start()
#         self.addCleanup(patcher.stop)

#         # Set up a dummy notification service that won't raise errors
#         dummy_service = MagicMock()
#         dummy_service.send_notification.return_value = None
#         self.mock_notification_service_creator.return_value = dummy_service

#         # Instantiate the facade so that OTPServiceImpl() uses the patched notification_service_creator.
#         self.facade = AuthenticationFacade()

#     @patch.object(OTPServiceImpl, "send_otp")
#     @patch.object(OTPServiceImpl, "verify_otp")
#     @patch.object(UserValidationServiceImpl, "user_exists")
#     @patch.object(UserValidationServiceImpl, "has_user_access")
#     @patch.object(JWTServiceImpl, "generate_token")
#     def test_authenticate_user(
#         self,
#         mock_generate_token,
#         mock_has_user_access,
#         mock_user_exists,
#         mock_verify_otp,
#         mock_send_otp,
#     ):
#         # Setup mocks:
#         # Simulate that the user does not exist initially.
#         mock_user_exists.return_value = False
#         # Simulate OTP verification success.
#         mock_verify_otp.return_value = True
#         # Simulate that the newly created user has access.
#         mock_has_user_access.return_value = True
#         # Simulate token generation.
#         mock_generate_token.return_value = {
#             "access": "fake_access_token",
#             "refresh": "fake_refresh_token",
#         }

#         # Request OTP (this will use the patched send_otp)
#         self.facade.request_otp("1234567890")
#         mock_send_otp.assert_called_once()

#         # Verify OTP and authenticate (this uses patched verify_otp and generate_token)
#         response = self.facade.verify_otp_and_authenticate("1234567890", "1234")
#         self.assertIn("tokens", response)
#         self.assertEqual(response["tokens"]["access"], "fake_access_token")
#         self.assertEqual(response["tokens"]["refresh"], "fake_refresh_token")
#         # Since user_exists was False, is_new_user should be True.
#         self.assertTrue(response["is_new_user"])
