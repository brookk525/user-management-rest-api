# Autor: Brooklyn Muñoz

from adapters.implementations.supabase_s3_adapter import SupabaseS3Adapter
from adapters.interfaces.storage_adapter import StorageAdapter
from services.interfaces.storage_service import StorageService


class StorageServiceImpl(StorageService):
    def __init__(self):
        self.storage_adapter: StorageAdapter = SupabaseS3Adapter()

    def upload_avatar(self, file_name: str, content: bytes, content_type: str) -> str:
        if file_name == "" or content is None:
            raise ValueError("El archivo no es valido")

        return self.storage_adapter.upload_avatar(file_name, content, content_type)
