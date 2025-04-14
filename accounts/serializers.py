from rest_framework import serializers


class OTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=6, required=False, allow_blank=True)
