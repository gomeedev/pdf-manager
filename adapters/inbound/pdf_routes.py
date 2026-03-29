from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

from core.security import require_auth
from core.ports.auth import AuthUser
from di.container import get_db_port, get_storage_port
from core.ports.database import DatabasePort
from core.ports.storage import StoragePort
from core.services.pdf_service import PDFService

router = APIRouter(prefix="/api/v1/pdf-ops", tags=["PDF Operations"])

def get_pdf_service(db: DatabasePort = Depends(get_db_port), storage: StoragePort = Depends(get_storage_port)) -> PDFService:
    return PDFService(db=db, storage=storage)

class MergeRequest(BaseModel):
    file_ids: List[uuid.UUID]
    output_filename: str

class SplitRequest(BaseModel):
    file_id: uuid.UUID
    pages: List[int]
    output_filename: str

class RemovePagesRequest(BaseModel):
    file_id: uuid.UUID
    pages_to_remove: List[int]
    output_filename: str

class CompressRequest(BaseModel):
    file_id: uuid.UUID
    output_filename: str

@router.post("/merge")
def merge(
    request: MergeRequest,
    user: AuthUser = Depends(require_auth),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    try:
        new_pdf = pdf_service.process_merge(user.id, request.file_ids, request.output_filename)
        return {"status": "success", "data": new_pdf}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/split")
def split(
    request: SplitRequest,
    user: AuthUser = Depends(require_auth),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    try:
        new_pdf = pdf_service.process_split(user.id, request.file_id, request.pages, request.output_filename)
        return {"status": "success", "data": new_pdf}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/remove-pages")
def remove_pages(
    request: RemovePagesRequest,
    user: AuthUser = Depends(require_auth),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    try:
        new_pdf = pdf_service.process_remove_pages(user.id, request.file_id, request.pages_to_remove, request.output_filename)
        return {"status": "success", "data": new_pdf}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/compress")
def compress(
    request: CompressRequest,
    user: AuthUser = Depends(require_auth),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    try:
        new_pdf = pdf_service.process_compress(user.id, request.file_id, request.output_filename)
        return {"status": "success", "data": new_pdf}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
