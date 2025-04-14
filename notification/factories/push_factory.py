from notification.factories.notification_factory import NotificationFactory


class PushNotificationFactory(NotificationFactory):
    """
    Factory for creating a Push Notification Service.
    """

    def create_notification_service(self):
        from notification.services.push_service import PushNotificationService

        return PushNotificationService()
