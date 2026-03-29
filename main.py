from fastapi import FastAPI, Depends
from core.config import settings
from core.security import require_auth
from core.ports.auth import AuthUser
from di.container import get_db_port
from core.ports.database import DatabasePort

app = FastAPI(
    title="PDF Manager API",
    description="API for managing PDFs powered by an AI Agent",
    version="1.0.0"
)

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
