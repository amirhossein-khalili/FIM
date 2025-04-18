# files/services/storage_service.py
import logging
import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings

from files.services.abstract_storage_service import StorageService

logger = logging.getLogger(__name__)


class S3StorageService(StorageService):
    """
    Service for interacting with AWS S3 for file storage.
    Includes generating presigned URLs and uploading files/file objects.
    """

    def __init__(self, s3_client=None):
        """
        Initializes the S3 client using settings from django.conf.
        """
        try:
            self.s3_client = s3_client or boto3.client(
                "s3",
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
                config=boto3.session.Config(signature_version="s3v4"),
            )
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            logger.debug("S3 client initialized successfully.")
        except NoCredentialsError:
            logger.error(
                "AWS credentials not found. Ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set."
            )
            self.s3_client = None
            self.bucket_name = None
        except Exception as e:
            logger.exception(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
            self.bucket_name = None

    def generate_presigned_url(self, file_path, expires_in=3600):
        """
        Generates a presigned URL for downloading an object from S3.

        Args:
            file_path (str): The key (path) of the file in the S3 bucket.
            expires_in (int): Expiration time for the URL in seconds. Default is 3600 (1 hour).

        Returns:
            str: The presigned URL, or None if an error occurred.
        """
        if not self.s3_client or not self.bucket_name:
            logger.error("S3 client not initialized. Cannot generate presigned URL.")
            return None
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=expires_in,
            )
            logger.info(f"Generated presigned URL for {file_path}")
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL for file {file_path}: {e}")
            return None
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred generating presigned URL for {file_path}: {e}"
            )
            return None

    def upload_file_or_object(self, s3_key, local_file_path=None, file_object=None):
        """
        Uploads a file to S3 either from a local path or a file-like object.

        Args:
            s3_key (str): The desired key (path including filename) for the file in S3.
            local_file_path (str, optional): The path to the file on the local system. Defaults to None.
            file_object (file-like object, optional): A file-like object opened in binary read mode ('rb'). Defaults to None.

        Returns:
            bool: True if upload was successful, False otherwise.

        Raises:
            ValueError: If neither local_file_path nor file_object is provided.
        """
        if not self.s3_client or not self.bucket_name:
            logger.error("S3 client not initialized. Cannot upload file.")
            return False

        if local_file_path and file_object:
            logger.warning(
                "Both local_file_path and file_object provided. Prioritizing file_object."
            )
            local_file_path = None  # Prioritize file object if both given
        elif not local_file_path and not file_object:
            raise ValueError("Either local_file_path or file_object must be provided.")

        try:
            if file_object:
                logger.info(
                    f"Attempting to upload file object to S3 bucket '{self.bucket_name}' with key '{s3_key}'"
                )
                # Use upload_fileobj for file-like objects
                self.s3_client.upload_fileobj(file_object, self.bucket_name, s3_key)
                logger.info(
                    f"Successfully uploaded file object to s3://{self.bucket_name}/{s3_key}"
                )
                return True
            elif local_file_path:
                if not os.path.exists(local_file_path):
                    logger.error(
                        f"Local file not found at {local_file_path}. Cannot upload."
                    )
                    return False
                logger.info(
                    f"Attempting to upload {local_file_path} to S3 bucket '{self.bucket_name}' with key '{s3_key}'"
                )
                # Use upload_file for local paths
                self.s3_client.upload_file(local_file_path, self.bucket_name, s3_key)
                logger.info(
                    f"Successfully uploaded {local_file_path} to s3://{self.bucket_name}/{s3_key}"
                )
                return True

        except ClientError as e:
            logger.error(f"S3 ClientError during upload to {s3_key}: {e}")
            return False
        except FileNotFoundError:
            # This should only happen if local_file_path was used and file disappeared
            logger.error(
                f"Local file {local_file_path} disappeared before upload could complete."
            )
            return False
        except NoCredentialsError:
            logger.error("AWS credentials not found during upload attempt.")
            return False
        except Exception as e:
            # Catch potential issues with file_object reading as well
            logger.exception(f"An unexpected error occurred uploading to {s3_key}: {e}")
            return False

        return False  # Should not be reached ideally

    # Keep the old method signature for potential compatibility, but make it use the new one
    def upload_file(self, local_file_path, s3_key):
        """
        Uploads a file from the local filesystem to S3. (Legacy wrapper)
        """
        return self.upload_file_or_object(
            s3_key=s3_key, local_file_path=local_file_path
        )
