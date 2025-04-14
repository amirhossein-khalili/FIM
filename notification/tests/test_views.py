from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from notification.models import Notification, NotificationType


class PushNotificationListViewTest(APITestCase):
    def setUp(self):
        # Create a test user with a phone field.
        User = get_user_model()
        self.user = User.objects.create_user(
            phone="1234567890",
            password="testpass",
        )
        self.client = APIClient()
        # Update the URL reverse to include the namespace:
        self.url = reverse("notification:in_app_notifications")

        # Create two push notifications for the test user's phone number.
        Notification.objects.create(
            recipient="1234567890",
            message="Push message 1",
            notification_type=NotificationType.PUSH,
            status=True,
        )
        Notification.objects.create(
            recipient="1234567890",
            message="Push message 2",
            notification_type=NotificationType.PUSH,
            status=True,
        )

        # Create a notification that should not be returned because it is not a push notification.
        Notification.objects.create(
            recipient="1234567890",
            message="Email message",
            notification_type=NotificationType.EMAIL,
            status=True,
        )

        # Create a push notification for another user (different phone number).
        Notification.objects.create(
            recipient="0987654321",
            message="Other user's push message",
            notification_type=NotificationType.PUSH,
            status=True,
        )

    def test_unauthenticated_access(self):
        """
        Ensure that unauthenticated users receive a 401 Unauthorized response.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_notifications_by_phone(self):
        """
        Verify that an authenticated user only gets their push notifications based on phone number,
        and that the response is paginated.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure that the response uses pagination.
        self.assertIn("results", response.data)
        results = response.data["results"]

        # Only two push notifications for phone "1234567890" should be returned.
        self.assertEqual(len(results), 2)

        for notification in results:
            self.assertEqual(notification["recipient"], "1234567890")
            # Ensure that notification_type is the display string for PUSH.
            self.assertEqual(notification["notification_type"], "Push")

        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
