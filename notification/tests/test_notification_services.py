import io
import sys

import requests
from django.core import mail
from django.test import TestCase, override_settings

from notification.models import Notification, NotificationType
from notification.services.dev_service import DevNotificationService
from notification.services.email_service import EmailNotificationService
from notification.services.push_service import PushNotificationService
from notification.services.sms_service import SMSNotificationService


class DummyResponse:
    status_code = 200

    def raise_for_status(self):
        pass


class TestDevNotificationService(TestCase):
    def test_send_notification_creates_notification(self):
        service = DevNotificationService()

        # Capture printed output to verify the development message
        captured_output = io.StringIO()
        sys.stdout = captured_output

        service.send_notification("dev@example.com", "Test message")
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Test message", output)

        # Verify that a Notification record was created with the correct attributes
        notification = Notification.objects.last()
        self.assertEqual(notification.recipient, "dev@example.com")
        self.assertEqual(notification.message, "Test message")
        self.assertEqual(notification.notification_type, NotificationType.DEV)


@override_settings(
    DEFAULT_SUBJECT_EMAIL="Test Subject", DEFAULT_FROM_EMAIL="noreply@example.com"
)
class TestEmailNotificationService(TestCase):
    def test_send_notification_success(self):
        service = EmailNotificationService()

        service.send_notification("email@example.com", "Email message")

        # Verify that the email was sent using Django's test email backend
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Test Subject")
        self.assertEqual(email.body, "Email message")

        # Verify that a Notification record was created correctly
        notification = Notification.objects.last()
        self.assertEqual(notification.recipient, "email@example.com")
        self.assertEqual(notification.message, "Email message")
        # Email service may use a string value for type depending on your implementation
        self.assertEqual(notification.notification_type, NotificationType.EMAIL.value)


@override_settings(FCM_SERVER_KEY="dummykey")
class TestPushNotificationService(TestCase):
    def setUp(self):
        # Monkey patch requests.post to simulate a successful FCM call
        self.original_post = requests.post
        requests.post = lambda *args, **kwargs: DummyResponse()

    def tearDown(self):
        requests.post = self.original_post

    def test_send_notification_success(self):
        service = PushNotificationService()

        service.send_notification("push_recipient", "Push message")

        # Verify that a Notification record was created correctly for push notifications
        notification = Notification.objects.last()
        self.assertEqual(notification.recipient, "push_recipient")
        self.assertEqual(notification.message, "Push message")
        self.assertEqual(notification.notification_type, NotificationType.PUSH)


class DummySMSProvider:
    def __init__(self):
        self.called = False

    def send_sms(self, recipient, message):
        self.called = True
        return True


class TestSMSNotificationService(TestCase):
    def test_send_notification_success(self):
        dummy_provider = DummySMSProvider()
        service = SMSNotificationService(dummy_provider)

        service.send_notification("sms@example.com", "SMS message")

        self.assertTrue(dummy_provider.called)

        # Verify that a Notification record was created correctly for SMS notifications
        notification = Notification.objects.last()
        self.assertEqual(notification.recipient, "sms@example.com")
        self.assertEqual(notification.message, "SMS message")
        self.assertEqual(notification.notification_type, NotificationType.SMS)
