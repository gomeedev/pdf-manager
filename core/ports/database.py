from typing import Protocol, List, Optional, Dict, Any
from uuid import UUID

class DatabasePort(Protocol):
    def get_pdf_file(self, file_id: UUID) -> Optional[Dict[str, Any]]:
        ...
        
    def create_pdf_file(self, user_id: UUID, filename: str, storage_path: str) -> Dict[str, Any]:
        ...

    def get_user_pdf_files(self, user_id: UUID) -> List[Dict[str, Any]]:
        ...

    def create_operation(self, pdf_file_id: UUID, op_type: str) -> Dict[str, Any]:
        ...
        
    def update_operation_status(self, operation_id: UUID, status: str, result_path: Optional[str] = None) -> Dict[str, Any]:
        ...

    def delete_pdf_file(self, user_id: UUID, pdf_file_id: UUID) -> bool:
        ...
