from notification.models import NotificationType
from notification.provider import notification_service_creator


class AdminAlertService:
    def __init__(self):
        pass

    def send_signup_notification(self, user):
        alert_sender = notification_service_creator(NotificationType.TELEGRAM)
        alert_sender.send_notification(
            "admin receiver", f"some one has been sign up the user information {user}"
        )
