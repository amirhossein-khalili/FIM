import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from files.models import File
from files.services.abstract_storage_service import StorageService

logger = logging.getLogger(__name__)


class S3StorageService(StorageService):
    def __init__(self, s3_client=None):
        self.s3_client = s3_client or boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=boto3.session.Config(signature_version="s3v4"),
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def generate_presigned_url(self, file_path, expires_in=3600):
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Error generating presigned URL for file {file_path}: {e}")
            return None
