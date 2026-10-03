import pytest
from backend.utils.docx_formatter import format_docx
from backend.utils.pdf_formatter import format_pdf
from backend.utils.html_formatter import format_html_preview
from backend.services.document_service import document_service
from backend.models import ExportRequest

def test_docx_formatter():
    title = "Test NDA"
    content = "1. CONFIDENTIALITY: Both parties agree not to disclose proprietary trade secrets.\n2. TERM: 24 months."
    table = [{"term": "Duration", "details": "24 months"}]
    
    buffer = format_docx(title, content, table, "Non-Disclosure Agreement (NDA)")
    bytes_val = buffer.getvalue()
    assert len(bytes_val) > 1000

def test_pdf_formatter():
    title = "Test Lease Agreement"
    content = "1. PREMISES: Flat 402, Green Glen Layout.\n2. RENT: ₹35,000 per month."
    table = [{"term": "Monthly Rent", "details": "₹35,000"}]
    
    buffer = format_pdf(title, content, table, "Residential Lease Agreement")
    bytes_val = buffer.getvalue()
    assert bytes_val.startswith(b"%PDF")
    assert len(bytes_val) > 1000

def test_html_formatter():
    html_out = format_html_preview("Freelance Contract", "1. SCOPE: Mobile app development.", [{"term": "Milestone 1", "details": "₹25,000"}])
    assert "LEGALEASE" in html_out
    assert "Freelance Contract" in html_out
    assert "Milestone 1" in html_out

def test_document_service_exports():
    req = ExportRequest(
        title="Consulting Agreement",
        document_type="Service Agreement",
        content="Section 1. Services provided by consultant.",
        summary_table=[{"term": "Rate", "details": "$100/hr"}]
    )
    txt = document_service.export_txt(req)
    assert "CONSULTING AGREEMENT" in txt
    assert "Service Agreement" in txt
    
    docx_buf, docx_name = document_service.export_docx(req)
    assert docx_name.endswith(".docx")
    assert len(docx_buf.getvalue()) > 1000
    
    pdf_buf, pdf_name = document_service.export_pdf(req)
    assert pdf_name.endswith(".pdf")
    assert pdf_buf.getvalue().startswith(b"%PDF")
