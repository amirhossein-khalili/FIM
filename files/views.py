from venv import logger

from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files.models import File
from files.repositories.file_repository import FileRepository
from files.serializers import FileSerializer, FileUploadSerializer
from files.services.storage_service import S3StorageService
from files.task import process_file_upload


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, file_repository=None, **kwargs):
        super().__init__(**kwargs)
        self.file_repository = file_repository or FileRepository()

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if file already exists (optional, based on your logic)
        # Note: This checks based on name and user before async processing starts.
        # Consider if duplicates are based on content hash later if needed.
        existing_file = self.file_repository.get_file_by_name(
            request.user, file_obj.name
        )
        if existing_file:
            # Decide how to handle existing files:
            # Option 1: Return existing file info (as before)
            serializer = FileUploadSerializer(
                existing_file
            )  # Use FileUploadSerializer for guid
            return Response(
                {"message": "File already exists", "file": serializer.data},
                status=status.HTTP_200_OK,  # Or 200 OK if just returning info
            )
            # Option 2: Reject upload
            # return Response(
            #     {"error": "A file with this name already exists."},
            #     status=status.HTTP_409_CONFLICT
            # )

        # Create the File model instance
        # The file is saved to the default storage (likely local temporary storage first)
        # by the FileField upon model saving.
        file_instance = File(original_name=file_obj.name, user=request.user)
        # Assign the file object to the field before saving the model instance
        file_instance.file = file_obj
        # --- Optional: Set initial status ---
        # file_instance.status = FileStatus.PENDING
        # ------------------------------------

        try:
            # Save the model instance. This will save the file to the location
            # defined by `upload_to` in your File model's FileField.
            # This path should be accessible by the Celery worker.
            self.file_repository.save_file(file_instance)  # Handles the model .save()
            logger.info(
                f"File model instance created (PK: {file_instance.pk}) and file saved locally for: {file_obj.name}"
            )
        except Exception as e:
            # Catch potential database errors or file saving errors during initial save
            logger.exception(
                f"Error saving initial file record for {file_obj.name}: {e}"
            )
            return Response(
                {"error": "Failed to initiate file upload process."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Trigger the asynchronous task
        try:
            process_file_upload.delay(file_instance.pk)
            logger.info(
                f"Celery task process_file_upload queued for File PK: {file_instance.pk}"
            )
        except Exception as e:
            # Handle errors during task queuing (e.g., broker connection issues)
            logger.exception(
                f"Error queuing Celery task for File PK {file_instance.pk}: {e}"
            )
            # Optional: Attempt to clean up the created File record and local file
            # try:
            #     if file_instance.file:
            #         default_storage.delete(file_instance.file.name)
            #     file_instance.delete()
            # except Exception as cleanup_e:
            #      logger.error(f"Error during cleanup after Celery queue failure for PK {file_instance.pk}: {cleanup_e}")

            return Response(
                {
                    "error": "Failed to queue file for processing. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Return a response indicating the upload is being processed
        # Use FileUploadSerializer to return just the GUID
        serializer = FileUploadSerializer(file_instance)
        return Response(
            {
                "message": "File upload received and is being processed.",
                "file": serializer.data,  # Return GUID
            },
            status=status.HTTP_202_ACCEPTED,  # 202 Accepted is appropriate for async processing
        )


class FileListView(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, file_repository=None, **kwargs):
        super().__init__(**kwargs)
        self.file_repository = file_repository or FileRepository()

    def get_queryset(self):
        return self.file_repository.get_user_files(self.request.user)


class FileUrlView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, file_repository=None, storage_service=None, **kwargs):
        super().__init__(**kwargs)
        self.file_repository = file_repository or FileRepository()
        self.storage_service = storage_service or S3StorageService()

    def get(self, request, guid):
        file_instance = self.file_repository.get_file_by_guid(guid, request.user)
        if not file_instance:
            return Response(
                {"error": "File not found or you don’t have access"},
                status=status.HTTP_404_NOT_FOUND,
            )

        presigned_url = self.storage_service.generate_presigned_url(
            file_instance.file.name
        )
        if presigned_url:
            return Response({"url": presigned_url})
        return Response(
            {"error": "Unable to generate URL"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
