from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.security import require_auth
from core.ports.auth import AuthUser
from di.container import get_db_port
from core.ports.database import DatabasePort
from adapters.inbound.pdf_routes import router as pdf_router
from adapters.inbound.agent_routes import router as agent_router

app = FastAPI(
    title="PDF Manager API",
    description="API for managing PDFs powered by an AI Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)
app.include_router(agent_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "port": settings.port}

@app.get("/api/v1/users/me")
def get_current_user(user: AuthUser = Depends(require_auth)):
    return {"user": {"id": user.id, "email": user.email}}

@app.get("/api/v1/pdfs")
def list_my_pdfs(
    user: AuthUser = Depends(require_auth),
    db: DatabasePort = Depends(get_db_port)
):
    pdfs = db.get_user_pdf_files(user.id)
    return {"data": pdfs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
