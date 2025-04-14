from rest_framework import generics, pagination, permissions

from notification.models import Notification, NotificationType
from notification.serializers import NotificationSerializer


class NotificationPagination(pagination.PageNumberPagination):
    """
    Custom pagination class for notifications.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class PushNotificationListView(generics.ListAPIView):
    """
    API endpoint for listing paginated in-app (push) notifications for the authenticated user.

    This view ensures that:
      - Only push notifications are returned.
      - Each user sees only notifications addressed to their phone number.
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        """
        Return a queryset of push notifications filtered by the authenticated user's phone number.
        """
        return Notification.objects.filter(
            notification_type=NotificationType.PUSH,
            recipient=self.request.user.phone,
        ).order_by("-sent_at")
