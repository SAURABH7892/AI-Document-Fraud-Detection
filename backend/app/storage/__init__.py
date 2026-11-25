"""Storage factory and accessors."""
from backend.app.core.config import settings
from backend.app.storage.base import StorageAdapter
from backend.app.storage.local import LocalStorageAdapter

_storage_instance: StorageAdapter = None

def get_storage() -> StorageAdapter:
    """Return configured storage adapter instance."""
    global _storage_instance
    if _storage_instance is None:
        if settings.STORAGE_TYPE.lower() == "s3" and settings.AWS_S3_BUCKET_NAME:
            try:
                from backend.app.storage.s3 import S3StorageAdapter
                _storage_instance = S3StorageAdapter()
            except Exception:
                _storage_instance = LocalStorageAdapter(settings.STORAGE_LOCAL_PATH)
        else:
            _storage_instance = LocalStorageAdapter(settings.STORAGE_LOCAL_PATH)
    return _storage_instance
