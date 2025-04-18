# accounts/urls.py
from django.urls import path

from .views import AdminApproveUserView, UserLoginView, UserSignupView

app_name = "accounts"
urlpatterns = [
    path("sign-up/", UserSignupView.as_view(), name="sign-up"),
    path("login/", UserLoginView.as_view(), name="login"),
]
