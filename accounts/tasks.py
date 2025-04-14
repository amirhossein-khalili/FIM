from celery import shared_task
from django.utils import timezone

from accounts.models import OTP


@shared_task
def delete_expired_otps():
    OTP.objects.filter(expires_at__lt=timezone.now()).delete()
