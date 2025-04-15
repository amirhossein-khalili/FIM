from django.core.exceptions import ValidationError
from rest_framework import serializers

from accounts.models import User


class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        # Check if the username already exists
        if User.objects.filter(user_name=value).exists():
            raise serializers.ValidationError(
                "Please choose another username. This one is already taken."
            )
        return value
