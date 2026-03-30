from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from uuid import UUID

from core.security import require_auth
from core.ports.auth import AuthUser
from di.container import get_db_port, get_storage_port
from core.ports.database import DatabasePort
from core.ports.storage import StoragePort
from core.services.pdf_service import PDFService
from agent.react_agent import PDFAgent
from core.limiter import limiter

router = APIRouter(prefix="/api/v1/agent", tags=["AI Agent"])

def get_pdf_agent(
    db: DatabasePort = Depends(get_db_port),
    storage: StoragePort = Depends(get_storage_port)
) -> PDFAgent:
    pdf_service = PDFService(db=db, storage=storage)
    return PDFAgent(pdf_service=pdf_service, db=db)

class ChatRequest(BaseModel):
    message: str
    message_history: List[Dict[str, Any]] = []

@router.post(
    "/chat",
    summary="Chat with AI Agent",
    description="Conversational endpoint for the ReAct Agent. It accepts a message and message_history and operates on the user's PDFs.",
    response_model=dict
)
@limiter.limit("20/minute")
def chat_with_agent(
    request: Request,
    chat_request: ChatRequest,
    user: AuthUser = Depends(require_auth),
    agent: PDFAgent = Depends(get_pdf_agent)
):
    reply, history = agent.chat(
        user_id=user.id,
        message=chat_request.message,
        message_history=chat_request.message_history
    )
    
    # Optional: we strip tool contents from history before sending to client if we want,
    # but returning it allows the client to keep state perfectly.
    # The client can pass it back unmutated.
    # Groq API uses 'tool_calls' on the assistant object, we should transform it into dict if necessary.
    # The SDK usually returns a dict if we format it right, but we need to ensure it's JSON serializable.
    
    # Helper to make history serializable securely
    serializable_history = []
    for msg in history:
        serializable_history.append({
            "role": msg.get("role"),
            "content": msg.get("content"),
            "name": msg.get("name"),
            "tool_call_id": msg.get("tool_call_id")
        })
        # Note: We omit tool_calls array to prevent client serialization issues 
        # unless dict-ified fully, we could do full parsing. 
        # Simple string passing is often safer for immediate history.
        
    return {
        "reply": reply,
        "history": serializable_history
    }
