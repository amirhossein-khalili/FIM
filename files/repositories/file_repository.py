from files.models import File, FileStatus


class FileRepository:
    def get_user_files(self, user):
        return File.objects.filter(user=user, status=FileStatus.COMPLETED)

    def get_file_by_guid(self, guid, user):
        try:
            return File.objects.get(guid=guid, user=user, status=FileStatus.COMPLETED)
        except File.DoesNotExist:
            return None

    def get_file_by_name(self, user, original_name):
        try:
            return File.objects.get(
                user=user, original_name=original_name, status=FileStatus.COMPLETED
            )
        except File.DoesNotExist:
            return None

    def save_file(self, file_instance):
        file_instance.save()
        return file_instance
