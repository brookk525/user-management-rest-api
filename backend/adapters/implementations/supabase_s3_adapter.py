# Autor: Brooklyn Muñoz

import os
from pathlib import Path
from uuid import uuid4

import boto3
from dotenv import load_dotenv

from adapters.interfaces.storage_adapter import StorageAdapter


class SupabaseS3Adapter(StorageAdapter):
    def __init__(self):
        # aqui cargo las claves de Supabase Storage desde el .env.
        env_path: Path = Path(__file__).parents[3] / ".env"
        load_dotenv(env_path)
        self.endpoint: str | None = os.getenv("SUPABASE_S3_ENDPOINT")
        self.region: str | None = os.getenv("SUPABASE_S3_REGION")
        self.access_key: str | None = os.getenv("SUPABASE_S3_ACCESS_KEY")
        self.secret_key: str | None = os.getenv("SUPABASE_S3_SECRET_KEY")
        self.bucket: str | None = os.getenv("SUPABASE_S3_BUCKET")

    def upload_avatar(self, file_name: str, content: bytes, content_type: str) -> str:
        if self.endpoint is None:
            raise ValueError("Falta el endpoint de Supabase Storage")
        if self.region is None:
            raise ValueError("Falta la region de Supabase Storage")
        if self.access_key is None:
            raise ValueError("Falta la access key de Supabase Storage")
        if self.secret_key is None:
            raise ValueError("Falta la secret key de Supabase Storage")
        if self.bucket is None:
            raise ValueError("Faltan variables de entorno de Supabase Storage")

        # aqui uso uuid4 para que dos avatares con el mismo nombre no se pisen.
        final_file_name: str = f"{uuid4()}-{file_name}"

        # aqui creo el cliente S3 usando la configuracion de Supabase.
        client = boto3.client(
            "s3",
            endpoint_url = self.endpoint,
            region_name = self.region,
            aws_access_key_id = self.access_key,
            aws_secret_access_key = self.secret_key,
        )

        # aqui subo el archivo al bucket de avatares.
        client.put_object(
            Bucket = self.bucket,
            Key = final_file_name,
            Body = content,
            ContentType = content_type,
        )

        # aqui devuelvo la URL publica para poder mostrar el avatar en el navegador.
        public_url: str = self.endpoint.replace(
            ".storage.supabase.co/storage/v1/s3",
            ".supabase.co/storage/v1/object/public",
        )
        return f"{public_url}/{self.bucket}/{final_file_name}"
