from typing import Dict, List

from notification.models import Notification


class NotificationMixin:
    """
    Mixin for retrieving notifications.
    """

    NOTIFICATION_TYPE = None

    def list_notifications(self) -> List[Dict[str, str]]:
        """
        Retrieve a list of sent notifications.
        """
        if not self.NOTIFICATION_TYPE:
            raise ValueError("NOTIFICATION_TYPE must be defined in the subclass.")

        notifications = Notification.objects.filter(
            notification_type=self.NOTIFICATION_TYPE
        ).order_by("-sent_at")

        return [
            {
                "recipient": n.recipient,
                "message": n.message,
                "sent_at": n.sent_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Sent" if n.status else "Failed",
            }
            for n in notifications
        ]
