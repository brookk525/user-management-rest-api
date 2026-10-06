# Autor: Brooklyn Muñoz

from abc import ABC, abstractmethod


class StorageAdapter(ABC):
    @abstractmethod
    def upload_avatar(self, file_name: str, content: bytes, content_type: str) -> str:
        pass
