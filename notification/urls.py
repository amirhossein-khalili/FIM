from django.urls import path

from notification.views import PushNotificationListView

app_name = "notification"

urlpatterns = [
    path("in-app/", PushNotificationListView.as_view(), name="in_app_notifications"),
]
