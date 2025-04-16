from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    def generate_presigned_url(self, file_path, expires_in=3600):
        pass
