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


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, file_repository=None, storage_service=None, **kwargs):
        super().__init__(**kwargs)
        self.file_repository = file_repository or FileRepository()
        self.storage_service = storage_service or S3StorageService()

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        existing_file = self.file_repository.get_file_by_name(
            request.user, file_obj.name
        )
        if existing_file:
            serializer = FileUploadSerializer(existing_file)
            return Response(
                {"message": "File already exists", "file": serializer.data},
                status=status.HTTP_200_OK,
            )

        file_instance = File(original_name=file_obj.name, user=request.user)
        file_instance.file.save(file_obj.name, file_obj, save=False)
        self.file_repository.save_file(file_instance)
        serializer = FileUploadSerializer(file_instance)
        return Response(
            {"message": "File uploaded successfully", "file": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class FileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, file_repository=None, storage_service=None, **kwargs):
        super().__init__(**kwargs)
        file_instance = self.file_repository.get_file_by_guid(guid, request.user)
        if not file_instance:
            return Response(
                {"error": "File not found or you don't have access"},
                status=status.HTTP_404_NOT_FOUND,
            )

        presigned_url = self.storage_service.generate_presigned_url(
            file_instance.file.name
        )
        if presigned_url:
            return HttpResponseRedirect(presigned_url)
        return Response(
            {"error": "Unable to access file"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
