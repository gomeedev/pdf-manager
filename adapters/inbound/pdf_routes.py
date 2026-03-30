from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from pydantic import BaseModel
from typing import List
import uuid

from core.security import require_auth
from core.ports.auth import AuthUser
from di.container import get_db_port, get_storage_port
from core.ports.database import DatabasePort
from core.ports.storage import StoragePort
from core.services.pdf_service import PDFService
from core.limiter import limiter

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

@router.post(
    "/merge",
    summary="Merge PDFs",
    description="Merges multiple PDFs in the specified list order into a single PDF.",
    response_model=dict
)
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

@router.post(
    "/split",
    summary="Split PDF pages",
    description="Extracts specific pages from a PDF to generate a new file.",
    response_model=dict
)
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

@router.post(
    "/remove-pages",
    summary="Remove PDF pages",
    description="Deletes specific pages from a PDF file.",
    response_model=dict
)
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

@router.post(
    "/compress",
    summary="Compress PDF",
    description="Compresses a PDF file to reduce storage footprint.",
    response_model=dict
)
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

@router.post(
    "/upload",
    summary="Upload PDF file",
    description="Uploads a raw PDF file to secure storage. Validates max 50MB size and PDF magic bytes.",
    response_model=dict
)
@limiter.limit("10/minute")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    user: AuthUser = Depends(require_auth),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """
    Uploads a raw PDF file into the user's Supabase bucket
    and registers it in the pdf_files table for future processing.
    """
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
            
        file_bytes = await file.read()
        
        # Validation 1: Size (50MB)
        if len(file_bytes) > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
            
        # Validation 2: Magic Bytes
        if not file_bytes.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Invalid PDF format: Missing magic bytes")
            
        new_pdf = pdf_service._save_result(file_bytes, user.id, file.filename)
        return {"status": "success", "data": new_pdf}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/{pdf_id}",
    summary="Delete PDF file",
    description="Deletes a user's PDF file from the database and storage entirely.",
    response_model=dict
)
def delete_pdf(
    pdf_id: uuid.UUID,
    user: AuthUser = Depends(require_auth),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    try:
        success = pdf_service.delete_pdf(user.id, pdf_id)
        if not success:
            raise HTTPException(status_code=404, detail="PDF not found or deletion failed")
        return {"status": "success", "detail": "PDF deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
