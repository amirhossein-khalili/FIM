import logging

from celery import shared_task
from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import File, FileStatus
from .services.storage_service import S3StorageService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_file_upload(self, file_pk):
    """
    Celery task to process the file upload asynchronously.
    - Sets status to PROCESSING.
    - Opens the file content and uploads it to S3 using upload_fileobj.
    - Updates the File model status to COMPLETED or FAILED.
    - Stores error message on failure.
    """

    file_instance = None
    try:
        with transaction.atomic():
            file_instance = get_object_or_404(File, pk=file_pk)

            if file_instance.status in [FileStatus.COMPLETED, FileStatus.FAILED]:
                logger.warning(
                    f"File PK: {file_pk} already processed with status: {file_instance.status}. Skipping."
                )
                return

            file_instance.status = FileStatus.PROCESSING
            file_instance.error_message = None
            file_instance.save(update_fields=["status", "error_message"])
            logger.info(
                f"Set status to PROCESSING for File PK: {file_pk} (GUID: {file_instance.guid})"
            )

        logger.info(f"Starting S3 upload processing for File: {file_instance.guid}")

        if not file_instance.file or not file_instance.file.name:
            logger.error(
                f"File reference (file.name) not found for File PK: {file_pk}."
            )
            with transaction.atomic():
                file_instance = File.objects.get(pk=file_pk)  # Re-fetch
                file_instance.status = FileStatus.FAILED
                file_instance.error_message = (
                    "Processing error: File reference missing."
                )
                file_instance.save(update_fields=["status", "error_message"])
            raise ValueError("File reference missing in model instance.")

        s3_key = file_instance.file.name

        storage_service = S3StorageService()
        upload_successful = False

        try:
            # !!! KEY CHANGE: Open the file from storage instead of getting path !!!
            with file_instance.file.open("rb") as file_obj:
                logger.info(f"Opened file object for {s3_key}. Attempting upload...")
                upload_successful = storage_service.upload_file_or_object(
                    s3_key=s3_key,
                    file_object=file_obj,
                )
        except FileNotFoundError:
            logger.error(
                f"File not found in storage backend for {s3_key} (PK: {file_pk}) when trying to open."
            )
            with transaction.atomic():
                file_instance = File.objects.get(pk=file_pk)  # Re-fetch
                file_instance.status = FileStatus.FAILED
                file_instance.error_message = (
                    "Processing error: Underlying file not found in storage."
                )
                file_instance.save(update_fields=["status", "error_message"])
            raise  # Re-raise FileNotFoundError
        except Exception as open_err:
            logger.exception(
                f"Error opening file {s3_key} (PK: {file_pk}) from storage: {open_err}"
            )
            with transaction.atomic():
                file_instance = File.objects.get(pk=file_pk)  # Re-fetch
                file_instance.status = FileStatus.FAILED
                file_instance.error_message = f"Processing error: Cannot read file from storage ({type(open_err).__name__})."
                file_instance.save(update_fields=["status", "error_message"])
            raise  # Re-raise the exception

        # --- Update status based on upload result ---
        with transaction.atomic():
            file_instance = File.objects.get(pk=file_pk)  # Re-fetch before final update
            if upload_successful:
                file_instance.status = FileStatus.COMPLETED
                file_instance.error_message = None
                file_instance.save(update_fields=["status", "error_message"])
                logger.info(
                    f"Successfully uploaded {s3_key} to S3. Set status to COMPLETED for File PK: {file_pk}"
                )

            else:
                # Ensure status is FAILED if upload returned False
                if file_instance.status != FileStatus.FAILED:
                    file_instance.status = FileStatus.FAILED
                    file_instance.error_message = (
                        "S3 upload failed (service returned False)."
                    )
                    file_instance.save(update_fields=["status", "error_message"])
                logger.error(
                    f"S3 upload failed for {s3_key}. Status set to FAILED for File PK: {file_pk}"
                )
                raise ConnectionError("S3 Upload failed (service returned False)")

    except File.DoesNotExist:
        logger.error(f"File with PK {file_pk} not found for processing.")
        return
    except Exception as e:
        logger.exception(
            f"Unhandled error processing file upload for PK {file_pk}: {e}"
        )
        if file_instance:
            try:
                with transaction.atomic():
                    file_instance = File.objects.get(pk=file_pk)
                    if file_instance.status != FileStatus.COMPLETED:
                        file_instance.status = FileStatus.FAILED
                        file_instance.error_message = (
                            f"Unexpected processing error: {str(e)[:255]}"
                        )
                        file_instance.save(update_fields=["status", "error_message"])
            except Exception as update_err:
                logger.error(
                    f"Failed to update file status to FAILED for PK {file_pk} during error handling: {update_err}"
                )

        # Retry the task based on decorator config
        try:
            # Raise the original exception 'e' to trigger retry with appropriate backoff
            raise self.retry(exc=e, countdown=int(60 * (self.request.retries + 1)))
        except self.MaxRetriesExceededError:
            logger.error(
                f"Max retries exceeded for processing file PK {file_pk}. Final status should be FAILED."
            )
