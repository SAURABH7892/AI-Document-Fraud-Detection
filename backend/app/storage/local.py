"""Local filesystem storage adapter."""
import os
import shutil
from pathlib import Path
from typing import BinaryIO
from backend.app.storage.base import StorageAdapter
from backend.app.core.config import settings

class LocalStorageAdapter(StorageAdapter):
    """Storage adapter implementation using local filesystem."""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or settings.STORAGE_LOCAL_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, storage_key: str) -> Path:
        # Prevent path traversal attacks
        clean_key = storage_key.lstrip("/\\")
        target_path = (self.base_path / clean_key).resolve()
        if not str(target_path).startswith(str(self.base_path)):
            raise ValueError(f"Path traversal detected: {storage_key}")
        return target_path

    def save(self, file_obj: BinaryIO, storage_key: str) -> str:
        target_path = self._resolve_path(storage_key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_path, "wb") as f:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            shutil.copyfileobj(file_obj, f)
        return storage_key

    def get(self, storage_key: str) -> bytes:
        target_path = self._resolve_path(storage_key)
        if not target_path.exists():
            raise FileNotFoundError(f"File not found in storage: {storage_key}")
        with open(target_path, "rb") as f:
            return f.read()

    def get_path(self, storage_key: str) -> str:
        target_path = self._resolve_path(storage_key)
        if not target_path.exists():
            raise FileNotFoundError(f"File not found in storage: {storage_key}")
        return str(target_path)

    def delete(self, storage_key: str) -> bool:
        target_path = self._resolve_path(storage_key)
        if target_path.exists():
            if target_path.is_file():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)
            return True
        return False

    def exists(self, storage_key: str) -> bool:
        return self._resolve_path(storage_key).exists()
