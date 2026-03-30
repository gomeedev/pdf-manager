from uuid import UUID
from typing import Optional, List, Dict, Any
from core.ports.database import DatabasePort
from supabase import Client

class SupabaseDatabaseAdapter(DatabasePort):
    def __init__(self, client: Client):
        self.client = client

    def get_pdf_file(self, file_id: UUID) -> Optional[Dict[str, Any]]:
        response = self.client.table("pdf_files").select("*").eq("id", str(file_id)).execute()
        return response.data[0] if response.data else None

    def create_pdf_file(self, user_id: UUID, filename: str, storage_path: str, size_bytes: int) -> Dict[str, Any]:
        data = {
            "user_id": str(user_id),
            "filename": filename,
            "storage_path": storage_path,
            "size_bytes": size_bytes
        }
        response = self.client.table("pdf_files").insert(data).execute()
        return response.data[0]

    def get_user_pdf_files(self, user_id: UUID) -> List[Dict[str, Any]]:
        response = self.client.table("pdf_files").select("*").eq("user_id", str(user_id)).execute()
        return response.data

    def create_operation(self, pdf_file_id: UUID, op_type: str) -> Dict[str, Any]:
        data = {
            "pdf_file_id": str(pdf_file_id),
            "type": op_type,
            "status": "pending"
        }
        response = self.client.table("operations").insert(data).execute()
        return response.data[0]

    def update_operation_status(self, operation_id: UUID, status: str, result_path: Optional[str] = None) -> Dict[str, Any]:
        data = {"status": status}
        if result_path is not None:
            data["result_path"] = result_path
        response = self.client.table("operations").update(data).eq("id", str(operation_id)).execute()
        return response.data[0]

    def delete_pdf_file(self, user_id: UUID, pdf_file_id: UUID) -> bool:
        self.client.table("operations").delete().eq("pdf_file_id", str(pdf_file_id)).execute()
        response = self.client.table("pdf_files").delete().eq("id", str(pdf_file_id)).eq("user_id", str(user_id)).execute()
        return len(response.data) > 0
