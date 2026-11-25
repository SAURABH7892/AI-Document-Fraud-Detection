"""S3-compatible object storage adapter."""
import io
import os
import tempfile
from typing import BinaryIO
from backend.app.storage.base import StorageAdapter
from backend.app.core.config import settings

class S3StorageAdapter(StorageAdapter):
    """Storage adapter implementation using AWS S3 or MinIO."""

    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL
            )
            self.bucket_name = settings.AWS_S3_BUCKET_NAME
        except Exception as e:
            raise RuntimeError(f"Failed to initialize S3 client: {e}")

    def save(self, file_obj: BinaryIO, storage_key: str) -> str:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        self.s3_client.upload_fileobj(file_obj, self.bucket_name, storage_key)
        return storage_key

    def get(self, storage_key: str) -> bytes:
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=storage_key)
        return response["Body"].read()

    def get_path(self, storage_key: str) -> str:
        # Download to temporary file for local processing
        temp_dir = tempfile.gettempdir()
        local_path = os.path.join(temp_dir, os.path.basename(storage_key))
        with open(local_path, "wb") as f:
            f.write(self.get(storage_key))
        return local_path

    def delete(self, storage_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=storage_key)
            return True
        except Exception:
            return False

    def exists(self, storage_key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_key)
            return True
        except Exception:
            return False
