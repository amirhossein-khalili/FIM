from rest_framework import serializers

from notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """

    notification_type = serializers.CharField(source="get_notification_type_display")

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "message",
            "notification_type",
            "sent_at",
            "status",
        ]
