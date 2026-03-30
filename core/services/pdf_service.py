import uuid
from typing import List
from core.ports.database import DatabasePort
from core.ports.storage import StoragePort
from core.domain.pdf_operations import merge_pdfs, split_pdf, compress_pdf, remove_pages

class PDFService:
    def __init__(self, db: DatabasePort, storage: StoragePort):
        self.db = db
        self.storage = storage

    def _download_files(self, file_ids: List[uuid.UUID]) -> List[bytes]:
        files_data = []
        for fid in file_ids:
            pdf_record = self.db.get_pdf_file(fid)
            if not pdf_record:
                raise ValueError(f"PDF file {fid} not found")
            
            storage_path = pdf_record["storage_path"]
            file_bytes = self.storage.download_file(storage_path)
            files_data.append(file_bytes)
        return files_data

    def _save_result(self, result_bytes: bytes, user_id: uuid.UUID, filename: str) -> dict:
        unique_path = f"{user_id}/{uuid.uuid4()}_{filename}"
        self.storage.upload_file(unique_path, result_bytes, "application/pdf")
        
        new_pdf = self.db.create_pdf_file(user_id=user_id, filename=filename, storage_path=unique_path)
        return new_pdf

    def process_merge(self, user_id: uuid.UUID, file_ids: List[uuid.UUID], output_filename: str) -> dict:
        files_bytes = self._download_files(file_ids)
        result_bytes = merge_pdfs(files_bytes)
        new_pdf = self._save_result(result_bytes, user_id, output_filename)
        self.db.create_operation(pdf_file_id=uuid.UUID(new_pdf["id"]), op_type="merge")
        return new_pdf

    def process_split(self, user_id: uuid.UUID, file_id: uuid.UUID, pages: List[int], output_filename: str) -> dict:
        files_bytes = self._download_files([file_id])
        result_bytes = split_pdf(files_bytes[0], pages)
        new_pdf = self._save_result(result_bytes, user_id, output_filename)
        self.db.create_operation(pdf_file_id=uuid.UUID(new_pdf["id"]), op_type="split")
        return new_pdf

    def process_remove_pages(self, user_id: uuid.UUID, file_id: uuid.UUID, pages: List[int], output_filename: str) -> dict:
        files_bytes = self._download_files([file_id])
        result_bytes = remove_pages(files_bytes[0], pages)
        new_pdf = self._save_result(result_bytes, user_id, output_filename)
        self.db.create_operation(pdf_file_id=uuid.UUID(new_pdf["id"]), op_type="remove_pages")
        return new_pdf

    def process_compress(self, user_id: uuid.UUID, file_id: uuid.UUID, output_filename: str) -> dict:
        files_bytes = self._download_files([file_id])
        result_bytes = compress_pdf(files_bytes[0])
        new_pdf = self._save_result(result_bytes, user_id, output_filename)
        self.db.create_operation(pdf_file_id=uuid.UUID(new_pdf["id"]), op_type="compress")
        return new_pdf

    def delete_pdf(self, user_id: uuid.UUID, file_id: uuid.UUID) -> bool:
        pdf_record = self.db.get_pdf_file(file_id)
        if not pdf_record or str(pdf_record["user_id"]) != str(user_id):
            raise ValueError(f"PDF file {file_id} not found or access denied")
        storage_path = pdf_record["storage_path"]
        db_deleted = self.db.delete_pdf_file(user_id, file_id)
        if db_deleted:
            try:
                self.storage.delete_file(storage_path)
            except Exception as e:
                pass
        return db_deleted
