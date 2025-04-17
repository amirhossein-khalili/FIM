from notification.factories.notification_factory import NotificationFactory


class TelegramBotServiceNotificationFactory(NotificationFactory):
    """
    Factory for creating an telegram bot Notification Service.
    """

    def create_notification_service(self):
        from notification.services.telegram_bot_service import (
            TelegramBotServiceNotification,
        )

        return TelegramBotServiceNotification()
