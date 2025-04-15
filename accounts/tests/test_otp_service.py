# import datetime
# from unittest.mock import MagicMock, patch

# from django.test import TestCase
# from django.utils import timezone

# from accounts.models import OTP
# from accounts.services.otp_service_impl import OTPServiceImpl


# class OTPServiceImplTest(TestCase):

#     def setUp(self):
#         self.phone = "1234567890"

#     @patch("accounts.services.otp_service_impl.notification_service_creator")
#     def test_send_otp(self, mock_notification_service_creator):
#         # Create a mock notification service with a send_notification method.
#         mock_notification_service = MagicMock()
#         mock_notification_service_creator.return_value = mock_notification_service

#         # Instantiate the OTP service (this calls notification_service_creator internally)
#         otp_service = OTPServiceImpl()

#         # Call send_otp and capture the response.
#         response = otp_service.send_otp(self.phone)
#         self.assertEqual(response["message"], "OTP sent successfully")

#         # Check if an OTP instance is stored in the database.
#         otp_instance = OTP.objects.get(phone=self.phone)
#         self.assertEqual(otp_instance.phone, self.phone)
#         self.assertIsInstance(otp_instance.code, str)
#         self.assertEqual(len(otp_instance.code), 4)

#         # Verify that the send_notification method was called with the correct parameters.
#         mock_notification_service.send_notification.assert_called_once_with(
#             recipient=self.phone, message=f"you otp code is \n {otp_instance.code}"
#         )

#     @patch("accounts.services.otp_service_impl.notification_service_creator")
#     def test_verify_otp_success(self, mock_notification_service_creator):
#         # Setup a mock notification service even if it's not used in verify.
#         mock_notification_service_creator.return_value = MagicMock()

#         # Instantiate the OTP service.
#         otp_service = OTPServiceImpl()

#         # Create a valid OTP instance with an expiration in the future.
#         otp_instance = OTP.objects.create(
#             phone=self.phone,
#             code="1234",
#             expires_at=timezone.now() + datetime.timedelta(minutes=10),
#         )

#         # Verify that providing the correct OTP returns True.
#         response = otp_service.verify_otp(self.phone, "1234")
#         self.assertTrue(response)

#         # Check that the OTP is marked as used.
#         otp_instance.refresh_from_db()
#         self.assertTrue(otp_instance.used)

#     @patch("accounts.services.otp_service_impl.notification_service_creator")
#     def test_verify_otp_failure(self, mock_notification_service_creator):
#         # Setup a mock notification service.
#         mock_notification_service_creator.return_value = MagicMock()

#         # Instantiate the OTP service.
#         otp_service = OTPServiceImpl()

#         # Create an OTP instance.
#         OTP.objects.create(
#             phone=self.phone,
#             code="1234",
#             expires_at=timezone.now() + datetime.timedelta(minutes=10),
#         )

#         # Verify that providing an incorrect OTP returns False.
#         response = otp_service.verify_otp(self.phone, "0000")
#         self.assertFalse(response)
