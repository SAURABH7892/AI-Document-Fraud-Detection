"""Abstract base storage adapter interface."""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class StorageAdapter(ABC):
    """Abstract interface for document and artifact storage."""

    @abstractmethod
    def save(self, file_obj: BinaryIO, storage_key: str) -> str:
        """Save a file object to storage and return its storage key/path."""
        pass

    @abstractmethod
    def get(self, storage_key: str) -> bytes:
        """Retrieve file bytes from storage."""
        pass

    @abstractmethod
    def get_path(self, storage_key: str) -> str:
        """Get absolute local filesystem path if available, or download locally."""
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    def exists(self, storage_key: str) -> bool:
        """Check if a file exists in storage."""
        pass
