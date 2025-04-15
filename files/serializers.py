# serializers.py
from rest_framework import serializers

from .models import File


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["file"]
        extra_kwargs = {"file": {"write_only": True}}

    def to_representation(self, instance):
        return {"guid": str(instance.guid)}


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["guid", "original_name", "uploaded_at"]
