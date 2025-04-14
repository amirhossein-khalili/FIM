# accounts/urls.py
from django.urls import path

from .views import AuthenticationView

app_name = "accounts"
urlpatterns = [
    path("auth/", AuthenticationView.as_view(), name="auth"),
]
