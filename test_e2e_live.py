import requests
import uuid
import sys

BASE_URL = "https://lincoln-quite-ratio-speech.trycloudflare.com"

def run_live_e2e():
    print(f"--- Running End-to-End Live Verification against {BASE_URL} ---")
    
    # 1. Health check
    res = requests.get(f"{BASE_URL}/health", timeout=10)
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"[PASS] 1. Health Check PASSED: {res.json()}")
    
    # 2. Root endpoint
    res = requests.get(f"{BASE_URL}/", timeout=10)
    assert res.status_code == 200
    print(f"[PASS] 2. Root Endpoint PASSED: {res.json()['project']} v{res.json()['version']}")
    
    # 3. Registration
    email1 = f"counsel_{uuid.uuid4().hex[:6]}@legalease.ai"
    reg_payload = {
        "email": email1,
        "password": "SecurePassword2026!",
        "full_name": "Senior Legal Counsel"
    }
    res = requests.post(f"{BASE_URL}/api/auth/register", json=reg_payload, timeout=10)
    assert res.status_code == 200, f"Registration failed: {res.text}"
    token1 = res.json()["access_token"]
    user1_id = res.json()["user"]["id"]
    print(f"[PASS] 3. User Registration PASSED for {email1} (User ID: {user1_id})")
    
    # 4. Login
    login_payload = {
        "email": email1,
        "password": "SecurePassword2026!"
    }
    res = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload, timeout=10)
    assert res.status_code == 200, f"Login failed: {res.text}"
    print(f"[PASS] 4. User Login PASSED")
    
    # 5. Google OAuth Login
    google_payload = {
        "email": f"partner_{uuid.uuid4().hex[:6]}@gmail.com",
        "full_name": "Managing Partner"
    }
    res = requests.post(f"{BASE_URL}/api/auth/google", json=google_payload, timeout=10)
    assert res.status_code == 200, f"Google OAuth failed: {res.text}"
    print(f"[PASS] 5. Google OAuth PASSED: {res.json()['user']['email']}")
    
    # 6. Document Generation (Employment Contract)
    gen_payload = {
        "document_type": "Employment Contract",
        "title": "Lead AI Architect Agreement",
        "party_a_name": "LegalEase Technologies Pvt. Ltd.",
        "party_a_role": "Employer",
        "party_a_address": "Level 14, Prestige Tech Park, Bangalore",
        "party_b_name": "Arun Kumar",
        "party_b_role": "Employee",
        "party_b_address": "Flat 402, Green Glen Layout, Bangalore",
        "effective_date": "2026-10-01",
        "duration": "12 months",
        "payment_terms": "₹50,000 per month payable on the 1st of each calendar month",
        "responsibilities": "Lead software engineering, AI legal pipeline architecture",
        "confidentiality_terms": "Strict non-disclosure of proprietary algorithms and trade secrets",
        "termination_terms": "30 days prior written notice by either party",
        "governing_law": "State of Karnataka, India",
        "dispute_resolution": "Binding arbitration in Bangalore"
    }
    res = requests.post(
        f"{BASE_URL}/generate",
        json=gen_payload,
        headers={"Authorization": f"Bearer {token1}"},
        timeout=15
    )
    assert res.status_code == 200, f"Generation failed: {res.text}"
    gen_data = res.json()
    assert "content" in gen_data
    assert "summary_table" in gen_data
    assert len(gen_data["summary_table"]) >= 5
    print(f"[PASS] 6. Document Generation PASSED: Generated {len(gen_data['content'])} characters with {len(gen_data['summary_table'])} key terms")
    
    # 7. Save Document
    save_payload = {
        "id": gen_data.get("id"),
        "title": "Lead AI Architect Agreement (Custom Edited)",
        "document_type": "Employment Contract",
        "content": gen_data["content"] + "\n\n10. AMENDMENT: Added custom retention bonus.",
        "summary_table": gen_data["summary_table"]
    }
    res = requests.post(
        f"{BASE_URL}/api/documents/save",
        json=save_payload,
        headers={"Authorization": f"Bearer {token1}"},
        timeout=10
    )
    assert res.status_code == 200, f"Save failed: {res.text}"
    saved_doc = res.json()["document"]
    print(f"[PASS] 7. Save Document PASSED (ID: {saved_doc['id']})")
    
    # 8. Document History
    res = requests.get(
        f"{BASE_URL}/api/documents/history",
        headers={"Authorization": f"Bearer {token1}"},
        timeout=10
    )
    assert res.status_code == 200, f"History failed: {res.text}"
    history_docs = res.json()["documents"]
    assert any(d["id"] == saved_doc["id"] for d in history_docs)
    print(f"[PASS] 8. Document History PASSED: Found {len(history_docs)} documents for user")
    
    # 9. TXT Export
    exp_payload = {
        "title": saved_doc["title"],
        "document_type": saved_doc["document_type"],
        "content": saved_doc["content"],
        "summary_table": saved_doc["summary_table"]
    }
    res = requests.post(f"{BASE_URL}/export/txt", json=exp_payload, timeout=10)
    assert res.status_code == 200
    assert "LEAD AI ARCHITECT AGREEMENT" in res.text
    print(f"[PASS] 9. TXT Export PASSED ({len(res.text)} bytes)")
    
    # 10. DOCX Export
    res = requests.post(f"{BASE_URL}/export/docx", json=exp_payload, timeout=10)
    assert res.status_code == 200
    assert len(res.content) > 1000
    print(f"[PASS] 10. DOCX Export PASSED ({len(res.content)} bytes)")
    
    # 11. PDF Export
    res = requests.post(f"{BASE_URL}/export/pdf", json=exp_payload, timeout=10)
    assert res.status_code == 200
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 1000
    print(f"[PASS] 11. PDF Export PASSED ({len(res.content)} bytes)")
    
    # 12. User Isolation Verification
    email2 = f"other_{uuid.uuid4().hex[:6]}@legalease.ai"
    reg2 = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email2, "password": "Password123!", "full_name": "Separate User"
    }, timeout=10).json()
    token2 = reg2["access_token"]
    
    # User 2 tries to access User 1's saved document
    forbidden_res = requests.get(
        f"{BASE_URL}/api/documents/{saved_doc['id']}",
        headers={"Authorization": f"Bearer {token2}"},
        timeout=10
    )
    assert forbidden_res.status_code == 404, "User isolation breach!"
    print(f"[PASS] 12. User Isolation PASSED: User 2 is strictly blocked from accessing User 1's documents")
    
    print("\n[SUCCESS] ALL 12 LIVE END-TO-END VERIFICATION CHECKS PASSED ON PUBLIC HTTPS API!")

if __name__ == "__main__":
    run_live_e2e()
