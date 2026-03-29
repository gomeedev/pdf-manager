from fastapi import FastAPI
from core.config import settings

app = FastAPI(
    title="PDF Manager API",
    description="API for managing PDFs powered by an AI Agent",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "port": settings.port}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
