import io
from typing import List, Dict, Any, Optional, Tuple
from backend.models import DocumentGenerateRequest, DocumentSaveRequest, ExportRequest
from backend.ai_core.gemini_generator import generate_document_ai
from backend.services.storage_service import storage_service
from backend.utils.docx_formatter import format_docx
from backend.utils.pdf_formatter import format_pdf
from backend.utils.html_formatter import format_html_preview
from backend.utils.sanitizer import sanitize_text, clean_filename
from backend.config import settings

class DocumentService:
    def generate(self, req: DocumentGenerateRequest, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates legal document using AI generator (with strict safety rules & fallback),
        returns structured document with content and terms table.
        """
        # Sanitize all string fields
        req.party_a_name = sanitize_text(req.party_a_name)
        req.party_b_name = sanitize_text(req.party_b_name)
        if req.party_a_address:
            req.party_a_address = sanitize_text(req.party_a_address)
        if req.party_b_address:
            req.party_b_address = sanitize_text(req.party_b_address)
        if req.payment_terms:
            req.payment_terms = sanitize_text(req.payment_terms)
        if req.responsibilities:
            req.responsibilities = sanitize_text(req.responsibilities)
        if req.confidentiality_terms:
            req.confidentiality_terms = sanitize_text(req.confidentiality_terms)
        if req.termination_terms:
            req.termination_terms = sanitize_text(req.termination_terms)
        if req.governing_law:
            req.governing_law = sanitize_text(req.governing_law)
        if req.dispute_resolution:
            req.dispute_resolution = sanitize_text(req.dispute_resolution)
        if req.additional_information:
            req.additional_information = sanitize_text(req.additional_information)

        content, summary_table = generate_document_ai(req)
        title = req.title or req.document_type
        
        # If user is authenticated, we automatically create an initial draft record
        doc_record = None
        if user_id:
            doc_record = storage_service.save_document(
                user_id=user_id,
                title=title,
                document_type=req.document_type,
                content=content,
                summary_table=summary_table,
                metadata={"generated_by": "ai"}
            )
            
        doc_id = doc_record["id"] if doc_record else "preview_mode"
        
        return {
            "id": doc_id,
            "document_type": req.document_type,
            "title": title,
            "content": content,
            "summary_table": summary_table,
            "html_preview": format_html_preview(title, content, summary_table, req.document_type),
            "created_at": doc_record["created_at"] if doc_record else "",
            "updated_at": doc_record["updated_at"] if doc_record else "",
            "disclaimer": settings.LEGAL_DISCLAIMER
        }

    def save(self, req: DocumentSaveRequest, user_id: str) -> Dict[str, Any]:
        """Saves or updates user's edited document"""
        clean_content = sanitize_text(req.content)
        saved = storage_service.save_document(
            user_id=user_id,
            title=req.title,
            document_type=req.document_type,
            content=clean_content,
            summary_table=req.summary_table or [],
            doc_id=req.id,
            metadata=req.metadata or {}
        )
        saved["html_preview"] = format_html_preview(saved["title"], saved["content"], saved["summary_table"], saved["document_type"])
        saved["disclaimer"] = settings.LEGAL_DISCLAIMER
        return saved

    def get_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Returns document history strictly for the authenticated user"""
        return storage_service.get_user_documents(user_id)

    def get_document(self, doc_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch document with user ownership check"""
        doc = storage_service.get_document_by_id(doc_id, user_id)
        if doc:
            doc["html_preview"] = format_html_preview(doc["title"], doc["content"], doc["summary_table"], doc["document_type"])
            doc["disclaimer"] = settings.LEGAL_DISCLAIMER
        return doc

    def delete_document(self, doc_id: str, user_id: str) -> bool:
        """Delete document belonging to user"""
        return storage_service.delete_document(doc_id, user_id)

    def export_txt(self, req: ExportRequest) -> str:
        """Export clean text document containing user's final edited content"""
        clean_content = sanitize_text(req.content)
        header = f"{req.title.upper()}\n{'=' * len(req.title)}\nDocument Type: {req.document_type}\n\n"
        footer = f"\n\n{'=' * 60}\nLEGAL DISCLAIMER:\n{settings.LEGAL_DISCLAIMER}\n{'=' * 60}\n"
        return header + clean_content + footer

    def export_docx(self, req: ExportRequest) -> Tuple[io.BytesIO, str]:
        """Export professional DOCX using python-docx"""
        clean_content = sanitize_text(req.content)
        buffer = format_docx(
            title=req.title,
            content=clean_content,
            summary_table=req.summary_table,
            document_type=req.document_type
        )
        filename = f"{clean_filename(req.title)}.docx"
        return buffer, filename

    def export_pdf(self, req: ExportRequest) -> Tuple[io.BytesIO, str]:
        """Export professional PDF using ReportLab"""
        clean_content = sanitize_text(req.content)
        buffer = format_pdf(
            title=req.title,
            content=clean_content,
            summary_table=req.summary_table,
            document_type=req.document_type
        )
        filename = f"{clean_filename(req.title)}.pdf"
        return buffer, filename

document_service = DocumentService()
