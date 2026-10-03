import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone

from backend.config import settings
from backend.routes import router
from backend.models import HealthCheckResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.PROJECT_SUBTITLE} - Enterprise AI Legal Technology Platform",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
# Allows production frontend origins and development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for logos and assets
if os.path.exists(settings.ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=str(settings.ASSETS_DIR)), name="assets")

# Include Application Router
app.include_router(router)

@app.get("/", tags=["General"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "subtitle": settings.PROJECT_SUBTITLE,
        "version": settings.VERSION,
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "generate": "POST /generate",
            "export_txt": "POST /export/txt",
            "export_docx": "POST /export/docx",
            "export_pdf": "POST /export/pdf",
            "auth_login": "POST /api/auth/login",
            "auth_register": "POST /api/auth/register",
            "auth_google": "POST /api/auth/google",
            "history": "GET /api/documents/history"
        },
        "disclaimer": settings.LEGAL_DISCLAIMER
    }

@app.get("/health", response_model=HealthCheckResponse, tags=["Monitoring"])
def health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_engine": "Google Gemini API + Deterministic Legal Fallback",
        "model": settings.GEMINI_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("backend.main:app", host=settings.HOST, port=port, reload=False)
