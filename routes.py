from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header, Response, status
from fastapi.responses import StreamingResponse, PlainTextResponse

from backend.models import (
    DocumentGenerateRequest,
    DocumentSaveRequest,
    ExportRequest,
    UserRegisterRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    PasswordResetRequest,
    TokenResponse,
    HealthCheckResponse
)
from backend.services.auth_service import auth_service
from backend.services.document_service import document_service
from backend.config import settings

router = APIRouter()

# Authentication Dependencies
def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Strict authentication dependency: requires valid Bearer token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required. Please sign in to LegalEase."
        )
    token = authorization.split(" ")[1]
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token. Please sign in again."
        )
    return payload

def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Optional authentication dependency for flexible demo / public generation"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        return auth_service.decode_token(token)
    return None

# ================= AUTHENTICATION ENDPOINTS =================

@router.post("/auth/register", response_model=TokenResponse)
@router.post("/api/auth/register", response_model=TokenResponse)
def register(req: UserRegisterRequest):
    try:
        return auth_service.register(req.email, req.password, req.full_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed.")

@router.post("/auth/login", response_model=TokenResponse)
@router.post("/api/auth/login", response_model=TokenResponse)
def login(req: UserLoginRequest):
    try:
        return auth_service.login(req.identifier, req.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed.")

@router.post("/auth/google", response_model=TokenResponse)
@router.post("/api/auth/google", response_model=TokenResponse)
def google_auth(req: GoogleAuthRequest):
    try:
        return auth_service.authenticate_google(req.email, req.full_name, req.id_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google authentication failed: {str(e)}")

@router.post("/auth/forgot-password")
@router.post("/auth/reset-password")
@router.post("/api/auth/forgot-password")
@router.post("/api/auth/reset-password")
def reset_password(req: PasswordResetRequest):
    try:
        success = auth_service.reset_password(req.identifier, req.new_password)
        return {"status": "success", "message": "Password reset successfully. Please log in with your new password."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password.")

@router.get("/api/auth/me")
def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "id": user["sub"],
        "email": user["email"],
        "full_name": user["name"],
        "role": user["role"]
    }

# ================= DOCUMENT GENERATION & MANAGEMENT =================

@router.post("/generate")
@router.post("/api/generate")
def generate_document(req: DocumentGenerateRequest, user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    """Generate legal document with AI engine and return preview"""
    user_id = user["sub"] if user else None
    try:
        result = document_service.generate(req, user_id=user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Document generation failed: {str(e)}")

@router.post("/api/documents/save")
def save_document(req: DocumentSaveRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Save or update user-specific document"""
    user_id = user["sub"]
    try:
        saved = document_service.save(req, user_id=user_id)
        return {"status": "success", "message": "Document saved successfully.", "document": saved}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save document: {str(e)}")

@router.get("/api/documents/history")
def get_document_history(user: Dict[str, Any] = Depends(get_current_user)):
    """Fetch all documents created by the currently authenticated user"""
    user_id = user["sub"]
    try:
        docs = document_service.get_history(user_id=user_id)
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve history.")

@router.get("/api/documents/{doc_id}")
def get_document(doc_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Fetch single document ensuring user ownership"""
    user_id = user["sub"]
    doc = document_service.get_document(doc_id, user_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or access denied.")
    return doc

@router.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Delete document owned by user"""
    user_id = user["sub"]
    success = document_service.delete_document(doc_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or access denied.")
    return {"status": "success", "message": "Document deleted successfully."}

# ================= DOCUMENT EXPORT ENDPOINTS =================

@router.post("/export/txt", response_class=PlainTextResponse)
@router.post("/api/export/txt", response_class=PlainTextResponse)
def export_txt(req: ExportRequest):
    """Export document as plain text"""
    try:
        text_content = document_service.export_txt(req)
        return text_content
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"TXT export failed: {str(e)}")

@router.post("/export/docx")
@router.post("/api/export/docx")
def export_docx(req: ExportRequest):
    """Export document as Microsoft Word DOCX"""
    try:
        buffer, filename = document_service.export_docx(req)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DOCX export failed: {str(e)}")

@router.post("/export/pdf")
@router.post("/api/export/pdf")
def export_pdf(req: ExportRequest):
    """Export document as Adobe PDF"""
    try:
        buffer, filename = document_service.export_pdf(req)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"PDF export failed: {str(e)}")
