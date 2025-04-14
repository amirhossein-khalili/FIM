from django.conf import settings

from notification.factories.notification_factory import NotificationFactory


class SMSNotificationFactory(NotificationFactory):
    """
    Factory for creating an SMS Notification Service.
    """

    def create_notification_service(self):
        from notification.services.sms_providers.development_sms_provider import (
            DevelopmentSMSProvider,
        )
        from notification.services.sms_providers.kavenegar_provider import (
            KavenegarSMSProvider,
        )
        from notification.services.sms_service import SMSNotificationService

        if settings.DEFAULT_SMS_PROVIDER == "development":
            sms_provider = DevelopmentSMSProvider()
        else:
            sms_provider = KavenegarSMSProvider()

        return SMSNotificationService(sms_provider)
