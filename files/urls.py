from django.urls import path

from .views import FileListView, FileUploadView, FileUrlView

app_name = "files"
urlpatterns = [
    path("upload/", FileUploadView.as_view(), name="file-upload"),
    # path("<uuid:guid>/", FileView.as_view(), name="file-view"),
    path("<uuid:guid>/url/", FileUrlView.as_view(), name="file-url"),
    path("list/", FileListView.as_view(), name="list"),
]
