from notification.factories.notification_factory import NotificationFactory
from notification.services.dev_service import DevNotificationService


class DevNotificationFactory(NotificationFactory):
    """
    Factory for creating a development notification service.
    """

    def create_notification_service(self):
        return DevNotificationService()
