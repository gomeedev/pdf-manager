from core.ports.storage import StoragePort
from core.config import settings
from supabase import Client

class SupabaseStorageAdapter(StoragePort):
    def __init__(self, client: Client):
        self.client = client
        self.bucket = settings.storage_bucket

    def upload_file(self, path: str, file_bytes: bytes, content_type: str) -> str:
        self.client.storage.from_(self.bucket).upload(
            path,
            file_bytes,
            file_options={"content-type": content_type, "upsert": "true"}
        )
        return path

    def download_file(self, path: str) -> bytes:
        return self.client.storage.from_(self.bucket).download(path)

    def delete_file(self, path: str) -> bool:
        response = self.client.storage.from_(self.bucket).remove([path])
        return len(response) > 0
