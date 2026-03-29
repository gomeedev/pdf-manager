from typing import Protocol

class StoragePort(Protocol):
    def upload_file(self, path: str, file_bytes: bytes, content_type: str) -> str:
        """Uploads a file to storage and returns the stored path/URL."""
        ...
        
    def download_file(self, path: str) -> bytes:
        """Downloads a file from storage."""
        ...
        
    def delete_file(self, path: str) -> bool:
        """Deletes a file from storage."""
        ...
