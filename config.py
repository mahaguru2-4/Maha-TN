import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "LegalEase"
    PROJECT_SUBTITLE: str = "AI-Powered Legal Document Generator"
    VERSION: str = "1.0.0"
    
    # AI / Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Default to current Gemini model; configurable
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    
    # Server / Network
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    BACKEND_URL: str = os.getenv("BACKEND_URL", f"http://localhost:{PORT}")
    
    # CORS
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]
    
    # Authentication & JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "legalease-production-secret-key-navy-gold-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "72"))
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Data Storage
    DATA_DIR: Path = BASE_DIR / "backend" / "data"
    DB_PATH: Path = DATA_DIR / "legalease.db"
    
    # Assets
    ASSETS_DIR: Path = BASE_DIR / "assets"
    LOGO_PATH: Path = ASSETS_DIR / "logo" / "legalease_logo.png"
    EMBLEM_PATH: Path = ASSETS_DIR / "logo" / "legalease_emblem.png"
    
    # Legal Disclaimer
    LEGAL_DISCLAIMER: str = (
        "LegalEase generates AI-assisted legal document drafts for informational and "
        "drafting purposes only. It does not provide legal advice and does not guarantee "
        "that a document is legally valid, enforceable, or suitable for your specific jurisdiction. "
        "Consider having all important legal documents reviewed by a qualified legal professional."
    )

settings = Settings()
os.makedirs(settings.DATA_DIR, exist_ok=True)
