from notification.factories.notification_factory import NotificationFactory


class EmailNotificationFactory(NotificationFactory):
    """
    Factory for creating an Email Notification Service.
    """

    def create_notification_service(self):
        from notification.services.email_service import EmailNotificationService

        return EmailNotificationService()
