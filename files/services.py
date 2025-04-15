import logging

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from files.models import File

# Set up logging
logger = logging.getLogger(__name__)


class FileService:
    """
    A service class for managing files in an S3-compatible storage system.
    Provides methods to list user files and generate presigned URLs for file access.
    """

    def __init__(self):
        """
        Initialize the S3 client with credentials and endpoint from Django settings.
        """
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=boto3.session.Config(signature_version="s3v4"),
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def get_user_files(self, user):
        """
        Retrieve a list of files belonging to the specified user from the database.

        Args:
            user: The User instance whose files should be retrieved.

        Returns:
            QuerySet: A Django QuerySet containing File objects for the user.
        """
        return File.objects.filter(user=user)

    def get_file_url(self, file, expires_in=3600):
        """
        Generate a presigned URL for temporary access to a file in S3 storage.

        Args:
            file: The File model instance for which to generate the URL.
            expires_in: Time in seconds until the URL expires (default: 1 hour).

        Returns:
            str or None: The presigned URL if successful, None if an error occurs.
        """
        print("inja?")
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file.file.name},
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            logger.error(f"Error generating presigned URL for file {file.guid}: {e}")
            return None
