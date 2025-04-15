# models.py
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class File(models.Model):
    def user_directory_path(instance, filename):
        return f"files/{instance.user.id}/{filename}"

    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.original_name

    class Meta:
        unique_together = (
            "user",
            "original_name",
        )
