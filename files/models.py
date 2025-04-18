import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _  # For choices


class FileStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    PROCESSING = "PROCESSING", _("Processing")
    COMPLETED = "COMPLETED", _("Completed")
    FAILED = "FAILED", _("Failed")


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
        related_name="files",
    )
    status = models.CharField(
        max_length=20,
        choices=FileStatus.choices,
        default=FileStatus.PENDING,
        db_index=True,
    )
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.original_name} ({self.get_status_display()})"

    class Meta:
        unique_together = ("user", "original_name")
        ordering = ["-uploaded_at"]
