import requests
from django.conf import settings

from notification.models import NotificationType
from notification.services.base import NotificationService
from notification.services.mixins import NotificationMixin


class PushNotificationService(NotificationMixin, NotificationService):
    """
    Sends push notifications using Firebase.
    """

    NOTIFICATION_TYPE = NotificationType.PUSH

    def __init__(self):
        self.fcm_api_url = "https://fcm.googleapis.com/fcm/send"
        self.fcm_server_key = settings.FCM_SERVER_KEY

    def _send(self, recipient: str, message: str) -> bool:
        """
        Sends a push notification via Firebase Cloud Messaging (FCM).
        """
        headers = {
            "Authorization": f"key={self.fcm_server_key}",
            "Content-Type": "application/json",
        }
        data = {
            "to": recipient,
            "notification": {"title": "New Notification", "body": message},
        }

        try:
            response = requests.post(self.fcm_api_url, json=data, headers=headers)
            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Failed to send push notification: {e}")
            return False
