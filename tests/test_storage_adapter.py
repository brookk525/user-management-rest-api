import sys
from types import ModuleType
from unittest.mock import Mock


try:
    import boto3  # noqa: F401
except ModuleNotFoundError:
    fake_boto3_module = ModuleType("boto3")
    fake_boto3_module.client = Mock()
    sys.modules["boto3"] = fake_boto3_module


from adapters.implementations import supabase_s3_adapter


def test_upload_avatar_sends_expected_data_to_s3(monkeypatch):
    monkeypatch.setenv(
        "SUPABASE_S3_ENDPOINT",
        "https://project.storage.supabase.co/storage/v1/s3",
    )
    monkeypatch.setenv("SUPABASE_S3_REGION", "eu-west-1")
    monkeypatch.setenv("SUPABASE_S3_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("SUPABASE_S3_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("SUPABASE_S3_BUCKET", "avatars")

    s3_client = Mock()
    monkeypatch.setattr(
        supabase_s3_adapter.boto3,
        "client",
        Mock(return_value=s3_client),
    )
    monkeypatch.setattr(
        supabase_s3_adapter,
        "uuid4",
        lambda: "fixed-uuid",
    )
    adapter = supabase_s3_adapter.SupabaseS3Adapter()

    avatar_url = adapter.upload_avatar(
        "avatar.png",
        b"image-content",
        "image/png",
    )

    supabase_s3_adapter.boto3.client.assert_called_once_with(
        "s3",
        endpoint_url="https://project.storage.supabase.co/storage/v1/s3",
        region_name="eu-west-1",
        aws_access_key_id="test-access-key",
        aws_secret_access_key="test-secret-key",
    )
    s3_client.put_object.assert_called_once_with(
        Bucket="avatars",
        Key="fixed-uuid-avatar.png",
        Body=b"image-content",
        ContentType="image/png",
    )
    assert avatar_url == (
        "https://project.supabase.co/storage/v1/object/public/"
        "avatars/fixed-uuid-avatar.png"
    )
