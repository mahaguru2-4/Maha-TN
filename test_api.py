import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["project"] == "LegalEase"
    assert data["status"] == "operational"
    assert "health_check" in data

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "LegalEase"

def test_auth_and_user_flow():
    import uuid
    email = f"testuser_{uuid.uuid4().hex[:8]}@legalease.ai"
    # Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Test Attorney"
    })
    assert reg_res.status_code == 200
    token = reg_res.json()["access_token"]
    assert token is not None
    
    # Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    
    # Me endpoint
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

def test_generate_document_endpoint():
    payload = {
        "document_type": "Employment Contract",
        "title": "Senior Engineer Contract",
        "party_a_name": "LegalEase Technologies Pvt. Ltd.",
        "party_a_role": "Employer",
        "party_b_name": "Arun Kumar",
        "party_b_role": "Employee",
        "effective_date": "2026-10-01",
        "duration": "12 months",
        "payment_terms": "₹50,000 per month",
        "responsibilities": "Full stack AI engineer"
    }
    res = client.post("/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "content" in data
    assert "summary_table" in data
    assert len(data["summary_table"]) > 0
    assert "LegalEase Technologies" in data["content"]
    assert "Arun Kumar" in data["content"]

def test_export_endpoints():
    export_payload = {
        "title": "Employment Contract",
        "document_type": "Employment Contract",
        "content": "THIS AGREEMENT is entered into between LegalEase and Arun Kumar.\n1. DUTIES: Software engineering.",
        "summary_table": [{"term": "Salary", "details": "₹50,000/mo"}]
    }
    
    # Test TXT export
    txt_res = client.post("/export/txt", json=export_payload)
    assert txt_res.status_code == 200
    assert "EMPLOYMENT CONTRACT" in txt_res.text
    
    # Test DOCX export
    docx_res = client.post("/export/docx", json=export_payload)
    assert docx_res.status_code == 200
    assert len(docx_res.content) > 1000
    
    # Test PDF export
    pdf_res = client.post("/export/pdf", json=export_payload)
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF")
