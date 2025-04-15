from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from files.services import FileService

from .models import File
from .serializers import FileSerializer, FileUploadSerializer


class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing file
        if File.objects.filter(user=request.user, original_name=file_obj.name).exists():
            existing_file = File.objects.get(
                user=request.user, original_name=file_obj.name
            )
            serializer = FileUploadSerializer(existing_file)
            return Response(
                {
                    "message": "File uploaded successfully",
                },
                status=status.HTTP_200_OK,
                # {"message": "File already exists", "file": serializer.data},
                # status=status.HTTP_200_OK,
            )

        # Upload new file
        file_instance = File(original_name=file_obj.name, user=request.user)
        file_instance.file.save(file_obj.name, file_obj, save=True)
        serializer = FileUploadSerializer(file_instance)
        return Response(
            {"message": "File uploaded successfully", "file": serializer.data},
            status=status.HTTP_201_CREATED,
        )


class FileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, guid):
        try:
            # ABAC: Ensure the file belongs to the requesting user
            file_instance = File.objects.get(guid=guid, user=request.user)

            # Initialize boto3 client for MinIO
            s3_client = boto3.client(
                "s3",
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
                use_ssl=settings.AWS_S3_USE_SSL,
            )

            # Generate presigned URL for the file
            file_key = file_instance.file.name  # e.g., "documents/filename.ext"
            try:
                presigned_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                        "Key": file_key,
                    },
                    ExpiresIn=3600,  # URL valid for 1 hour
                )
                # Redirect to the presigned URL for immediate download/view
                return HttpResponseRedirect(presigned_url)
            except ClientError as e:
                return Response(
                    {"error": "Unable to access file"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except File.DoesNotExist:
            return Response(
                {"error": "File not found or you don't have access"},
                status=status.HTTP_404_NOT_FOUND,
            )


class FileListView(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        service = FileService()
        return service.get_user_files(self.request.user)


class FileUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guid):
        try:
            file_instance = File.objects.get(guid=guid, user=request.user)
            service = FileService()
            presigned_url = service.get_file_url(file_instance)
            if presigned_url:
                return Response({"url": presigned_url})
            else:
                return Response({"error": "Unable to generate URL"}, status=500)
        except File.DoesNotExist:
            return Response(
                {"error": "File not found or you don’t have access"}, status=404
            )
