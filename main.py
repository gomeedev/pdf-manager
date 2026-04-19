from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.security import require_auth
from core.ports.auth import AuthUser
from di.container import get_db_port
from core.ports.database import DatabasePort
from adapters.inbound.pdf_routes import router as pdf_router
from adapters.inbound.agent_routes import router as agent_router
from fastapi import Request
from fastapi.responses import JSONResponse
import time
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from core.limiter import limiter
from core.logger import logger

app = FastAPI(
    title="PDF Manager API",
    description="API for managing PDFs powered by an AI Agent",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

class LogRequestsASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.time()
        status_code = [500]

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code[0] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            logger.exception(f"Unhandled exception in ASGI: {str(e)}")
            raise
        finally:
            process_time = time.time() - start_time
            logger.info(f"{scope['method']} {scope['path']} - Status: {status_code[0]} - Time: {process_time:.4f}s")

app.add_middleware(LogRequestsASGIMiddleware)
app.add_middleware(SlowAPIMiddleware)

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
