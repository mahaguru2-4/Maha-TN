import os
import uvicorn
from backend.config import settings

if __name__ == "__main__":
    port = int(os.environ.get("PORT", settings.PORT))
    print(f"Starting LegalEase FastAPI Backend on http://0.0.0.0:{port}...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, log_level="info")
