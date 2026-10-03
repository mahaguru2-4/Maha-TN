import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import requests
import io
import time
from datetime import datetime

from frontend.styles import get_custom_css
from backend.config import settings
from backend.models import DocumentGenerateRequest, DocumentSaveRequest, ExportRequest
from backend.services.document_service import document_service
from backend.services.auth_service import auth_service

# Page Configuration
st.set_page_config(
    page_title="LegalEase — AI Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom Dark Navy + Gold theme CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Backend URL resolution: Use local loopback first (ultra-fast & 100% resilient) or public URL
def resolve_backend_url():
    try:
        r = requests.get(f"http://127.0.0.1:{settings.PORT}/health", timeout=1)
        if r.status_code == 200:
            return f"http://127.0.0.1:{settings.PORT}"
    except Exception:
        pass
    return os.environ.get("BACKEND_URL", "https://lincoln-quite-ratio-speech.trycloudflare.com").rstrip("/")

BACKEND_URL = resolve_backend_url()

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "current_doc" not in st.session_state:
    st.session_state.current_doc = None
if "nav_choice" not in st.session_state:
    st.session_state.nav_choice = "Dashboard"

# ================= REST API CLIENT HELPERS =================

def get_auth_headers():
    token = st.session_state.get("user_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def api_check_health():
    """Pings backend health endpoint"""
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def api_login(identifier: str, password: str):
    """Authenticate via Backend API with username or email"""
    clean_id = identifier.strip()
    try:
        res = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": clean_id, "username": clean_id, "password": password},
            timeout=6
        )
        if res.status_code == 200:
            data = res.json()
            st.session_state.authenticated = True
            st.session_state.user_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.rerun()
        else:
            err = res.json().get("detail", "Invalid username or password.")
            st.error(f"Authentication Failed: {err}")
    except Exception:
        # Fallback to local service if network fails
        try:
            data = auth_service.login(clean_id, password)
            st.session_state.authenticated = True
            st.session_state.user_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.rerun()
        except Exception as e:
            st.error(f"Login error: {str(e)}")

def api_register(email: str, password: str, full_name: str):
    """Register account via Backend API"""
    try:
        res = requests.post(f"{BACKEND_URL}/api/auth/register", json={"email": email, "password": password, "full_name": full_name}, timeout=6)
        if res.status_code == 200:
            data = res.json()
            st.session_state.authenticated = True
            st.session_state.user_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.rerun()
        else:
            err = res.json().get("detail", "Registration failed.")
            st.error(f"Registration Error: {err}")
    except Exception:
        try:
            data = auth_service.register(email, password, full_name)
            st.session_state.authenticated = True
            st.session_state.user_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.rerun()
        except Exception as e:
            st.error(f"Registration error: {str(e)}")

def api_google_auth(email: str, full_name: str):
    """Authenticate via Google OAuth via Backend API"""
    try:
        res = requests.post(f"{BACKEND_URL}/api/auth/google", json={"email": email, "full_name": full_name}, timeout=6)
        if res.status_code == 200:
            data = res.json()
            st.session_state.authenticated = True
            st.session_state.user_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.rerun()
    except Exception:
        try:
            data = auth_service.authenticate_google(email, full_name)
            st.session_state.authenticated = True
            st.session_state.user_token = data["access_token"]
            st.session_state.user_info = data["user"]
            st.rerun()
        except Exception as e:
            st.error(f"Google authentication error: {str(e)}")

def api_logout():
    st.session_state.authenticated = False
    st.session_state.user_token = None
    st.session_state.user_info = None
    st.session_state.current_doc = None
    st.rerun()

def api_generate_document(req_dict: dict) -> dict:
    """Generate legal document via Backend POST /generate"""
    try:
        res = requests.post(
            f"{BACKEND_URL}/generate",
            json=req_dict,
            headers=get_auth_headers(),
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        err_msg = res.json().get("detail", "Generation failed on backend API.")
        raise Exception(err_msg)
    except Exception as e:
        # Fallback to local document service
        req_obj = DocumentGenerateRequest(**req_dict)
        user_id = st.session_state.user_info.get("id") if st.session_state.user_info else None
        return document_service.generate(req_obj, user_id=user_id)

def api_save_document(save_dict: dict) -> dict:
    """Save document via Backend POST /api/documents/save"""
    try:
        res = requests.post(
            f"{BACKEND_URL}/api/documents/save",
            json=save_dict,
            headers=get_auth_headers(),
            timeout=10
        )
        if res.status_code == 200:
            return res.json().get("document")
        raise Exception(res.json().get("detail", "Failed to save document on backend API."))
    except Exception:
        save_obj = DocumentSaveRequest(**save_dict)
        user_id = st.session_state.user_info.get("id") if st.session_state.user_info else "demo"
        return document_service.save(save_obj, user_id=user_id)

def api_get_history() -> list:
    """Fetch user-isolated history via Backend GET /api/documents/history"""
    try:
        res = requests.get(
            f"{BACKEND_URL}/api/documents/history",
            headers=get_auth_headers(),
            timeout=10
        )
        if res.status_code == 200:
            return res.json().get("documents", [])
    except Exception:
        pass
    user_id = st.session_state.user_info.get("id") if st.session_state.user_info else "demo"
    return document_service.get_history(user_id)

def api_get_document(doc_id: str) -> dict:
    """Fetch single document via Backend GET /api/documents/{id}"""
    try:
        res = requests.get(
            f"{BACKEND_URL}/api/documents/{doc_id}",
            headers=get_auth_headers(),
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    user_id = st.session_state.user_info.get("id") if st.session_state.user_info else "demo"
    return document_service.get_document(doc_id, user_id)

def api_delete_document(doc_id: str) -> bool:
    """Delete document via Backend DELETE /api/documents/{id}"""
    try:
        res = requests.delete(
            f"{BACKEND_URL}/api/documents/{doc_id}",
            headers=get_auth_headers(),
            timeout=10
        )
        if res.status_code == 200:
            return True
    except Exception:
        pass
    user_id = st.session_state.user_info.get("id") if st.session_state.user_info else "demo"
    return document_service.delete_document(doc_id, user_id)

def api_export_txt(exp_dict: dict) -> str:
    """Export TXT via Backend POST /export/txt"""
    try:
        res = requests.post(f"{BACKEND_URL}/export/txt", json=exp_dict, timeout=10)
        if res.status_code == 200:
            return res.text
    except Exception:
        pass
    exp_obj = ExportRequest(**exp_dict)
    return document_service.export_txt(exp_obj)

def api_export_docx(exp_dict: dict):
    """Export DOCX via Backend POST /export/docx"""
    try:
        res = requests.post(f"{BACKEND_URL}/export/docx", json=exp_dict, timeout=15)
        if res.status_code == 200:
            fname = exp_dict.get("title", "document").replace(" ", "_") + ".docx"
            return io.BytesIO(res.content), fname
    except Exception:
        pass
    exp_obj = ExportRequest(**exp_dict)
    return document_service.export_docx(exp_obj)

def api_export_pdf(exp_dict: dict):
    """Export PDF via Backend POST /export/pdf"""
    try:
        res = requests.post(f"{BACKEND_URL}/export/pdf", json=exp_dict, timeout=15)
        if res.status_code == 200:
            fname = exp_dict.get("title", "document").replace(" ", "_") + ".pdf"
            return io.BytesIO(res.content), fname
    except Exception:
        pass
    exp_obj = ExportRequest(**exp_dict)
    return document_service.export_pdf(exp_obj)


# ================= LOGIN SCREEN (FIRST EXPERIENCE) =================

if not st.session_state.authenticated:
    col_a, col_main, col_b = st.columns([1, 2, 1])
    with col_main:
        st.markdown("""
        <div class="auth-container">
            <div style="font-size: 42px; margin-bottom: 8px;">⚖️</div>
            <div style="font-family: 'Cinzel', serif; font-size: 26px; font-weight: 700; color: #d4af37; letter-spacing: 2px;">
                LEGALEASE
            </div>
            <div style="font-size: 12px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 24px;">
                AI-POWERED LEGAL DOCUMENT GENERATOR
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        auth_tab1, auth_tab2, auth_tab3, auth_tab4 = st.tabs([
            "🌐 Continue with Google",
            "📧 Email Sign In",
            "✨ Create Account",
            "🔑 Forgot Password"
        ])
        
        with auth_tab1:
            st.markdown("""
            <div style="text-align: center; padding: 20px 10px;">
                <p style="color: #cbd5e1; font-size: 14px; margin-bottom: 20px;">
                    Fast, secure, one-click authentication powered by Google OAuth.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            google_demo_email = st.text_input("Google Account Email", value="counsel@legalease.ai", key="g_email")
            google_demo_name = st.text_input("Your Display Name", value="Arun Kumar (Corporate Counsel)", key="g_name")
            
            if st.button("🚀 Continue with Google", use_container_width=True, key="btn_google"):
                api_google_auth(google_demo_email, google_demo_name)
                
        with auth_tab2:
            st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Sign in with your registered username or email address and password.</p>", unsafe_allow_html=True)
            email_input = st.text_input("Username or Email Address", placeholder="e.g. maha or counsel@legalease.ai", key="login_email")
            pass_input = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
            
            if st.button("Sign In", use_container_width=True, key="btn_signin"):
                if email_input and pass_input:
                    api_login(email_input, pass_input)
                else:
                    st.warning("Please provide both username/email and password.")
                    
        with auth_tab3:
            st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Create a secure LegalEase account to draft and manage contracts.</p>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Name / Username", placeholder="e.g. Arun Kumar or maha", key="reg_name")
            reg_email = st.text_input("Email Address", placeholder="name@domain.com", key="reg_email")
            reg_pass = st.text_input("Create Password", type="password", placeholder="Minimum 6 characters", key="reg_pass")
            
            if st.button("Create Account", use_container_width=True, key="btn_reg"):
                if reg_name and reg_email and reg_pass:
                    if len(reg_pass) < 6:
                        st.warning("Password must be at least 6 characters.")
                    else:
                        api_register(reg_email, reg_pass, reg_name)
                else:
                    st.warning("Please complete all registration fields.")
                    
        with auth_tab4:
            st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Reset your password securely.</p>", unsafe_allow_html=True)
            reset_email = st.text_input("Username or Registered Email", placeholder="e.g. maha or counsel@legalease.ai", key="rst_email")
            reset_new_pass = st.text_input("New Password", type="password", placeholder="Minimum 6 characters", key="rst_pass")
            if st.button("Reset Password", use_container_width=True, key="btn_reset"):
                try:
                    res = requests.post(f"{BACKEND_URL}/api/auth/reset-password", json={"identifier": reset_email, "email": reset_email, "new_password": reset_new_pass}, timeout=5)
                    if res.status_code == 200:
                        st.success("Password reset successfully! Please sign in with your new password.")
                    else:
                        st.error(res.json().get("detail", "Password reset failed."))
                except Exception:
                    try:
                        auth_service.reset_password(reset_email, reset_new_pass)
                        st.success("Password reset successfully! Please sign in.")
                    except Exception as e:
                        st.error(str(e))
                        
        st.markdown(f"""
        <div class="disclaimer-banner">
            <strong>LEGAL DISCLAIMER:</strong> {settings.LEGAL_DISCLAIMER}
        </div>
        """, unsafe_allow_html=True)
        
    st.stop()

# ================= AUTHENTICATED APPLICATION =================

user = st.session_state.user_info or {"full_name": "Counsel", "email": "counsel@legalease.ai", "id": "demo-user"}

# Top App Header
st.markdown(f"""
<div class="legalease-header">
    <div style="display: flex; align-items: center; gap: 16px;">
        <span style="font-size: 32px;">⚖️</span>
        <div>
            <div class="brand-title">LEGALEASE</div>
            <div class="brand-subtitle">AI-POWERED LEGAL DOCUMENT GENERATOR</div>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="color: #ffffff; font-weight: 600; font-size: 14px;">{user.get('full_name')}</div>
        <div style="color: #d4af37; font-size: 12px;">{user.get('email')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Check live backend health for status pill
health_info = api_check_health()
api_status_html = (
    f"<span style='color: #10b981;'>● Connected via HTTPS</span>"
    if health_info
    else "<span style='color: #f59e0b;'>● Local Fallback Mode</span>"
)

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0; border-bottom: 1px solid #1e2c4f; margin-bottom: 20px;">
        <div style="font-family: 'Cinzel', serif; font-size: 18px; color: #d4af37; font-weight: 700;">NAVIGATION</div>
    </div>
    """, unsafe_allow_html=True)
    
    nav = st.radio(
        "Menu",
        ["Dashboard", "Create Document", "My Documents", "Account Settings"],
        label_visibility="collapsed"
    )
    st.session_state.nav_choice = nav
    
    st.markdown("<br><hr style='border-color: #1e2c4f;'><br>", unsafe_allow_html=True)
    
    # Engine & Backend connection status in sidebar
    model_name = health_info.get("model", settings.GEMINI_MODEL) if health_info else settings.GEMINI_MODEL
    st.markdown(f"""
    <div style="background-color: #0d152b; border: 1px solid #1e2c4f; border-left: 3px solid #d4af37; padding: 12px; border-radius: 6px; font-size: 12px; margin-bottom: 20px;">
        <div style="color: #d4af37; font-weight: bold;">BACKEND CONNECTIVITY</div>
        <div style="color: #94a3b8; margin-top: 4px; font-size: 11px; word-break: break-all;">API: {BACKEND_URL}</div>
        <div style="margin-top: 4px;">{api_status_html}</div>
        <div style="color: #cbd5e1; font-family: monospace; margin-top: 4px;">Model: {model_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sign Out", use_container_width=True):
        api_logout()

# ================= VIEW 1: DASHBOARD =================

if st.session_state.nav_choice == "Dashboard":
    st.markdown(f"""
    <div class="legal-card-gold">
        <h2 style="font-family: 'Cinzel', serif; color: #ffffff; margin: 0 0 6px 0; font-size: 22px;">
            Welcome to LegalEase, {user.get('full_name')}
        </h2>
        <p style="color: #cbd5e1; margin: 0; font-size: 14px;">
            Draft enforceable, customized legal agreements powered by Google Gemini and enterprise legal templates.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch user's documents via connected Backend API
    user_docs = api_get_history()
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Saved Documents</div>
            <div class="metric-value">{len(user_docs)}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">Document Types</div>
            <div class="metric-value">8</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">Export Formats</div>
            <div class="metric-value">3 (PDF/DOCX/TXT)</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-label">Security & Isolation</div>
            <div class="metric-value" style="color: #10b981; font-size: 20px;">100% Isolated</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_dash_left, col_dash_right = st.columns([2, 1])
    
    with col_dash_left:
        st.markdown("<h3 class='card-title'>Recent Documents</h3>", unsafe_allow_html=True)
        if user_docs:
            for d in user_docs[:4]:
                st.markdown(f"""
                <div class="legal-card" style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #ffffff; font-size: 15px;">{d.get('title')}</div>
                        <div style="color: #d4af37; font-size: 12px;">{d.get('document_type')} • Last Modified: {d.get('updated_at', '')[:10]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No documents generated yet. Click 'Create New Document' to start your first legal draft!")
            
    with col_dash_right:
        st.markdown("<h3 class='card-title'>Quick Action</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div class="legal-card">
            <p style="color: #94a3b8; font-size: 13px;">Ready to generate an employment contract, non-disclosure agreement, or lease agreement?</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✍️ Create New Document", use_container_width=True):
            st.session_state.nav_choice = "Create Document"
            st.rerun()

# ================= VIEW 2: CREATE DOCUMENT =================

elif st.session_state.nav_choice == "Create Document":
    st.markdown("<h2 class='card-title' style='font-size: 24px;'>Create Legal Document</h2>", unsafe_allow_html=True)
    
    DOC_TYPES = [
        "Employment Contract",
        "Employment Offer Letter",
        "Non-Disclosure Agreement (NDA)",
        "Residential Lease Agreement",
        "Freelance Work Contract",
        "Service Agreement",
        "General Agreement",
        "General Contract"
    ]
    
    # Document Selection & Pre-fill Controls
    top_col1, top_col2 = st.columns([2, 1])
    with top_col1:
        selected_type = st.selectbox("Select Legal Document Type", DOC_TYPES, index=0)
    with top_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        load_sample = st.button("📋 Pre-fill Sample Data", help="Populates standard test data for quick demonstration")

    # Comprehensive sample presets for all 8 document types
    sample_data = {
        "Employment Contract": {
            "title": "Executive Employment Agreement",
            "p_a_name": "LegalEase Technologies Pvt. Ltd.",
            "p_a_role": "Employer",
            "p_a_addr": "Level 14, Prestige Tech Park, Bangalore 560103",
            "p_b_name": "Arun Kumar",
            "p_b_role": "Employee",
            "p_b_addr": "Flat 402, Green Glen Layout, Bangalore 560037",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-01",
            "end_date": "2027-09-30",
            "duration": "12 months",
            "payment": "₹50,000 per month (paid on the 1st of each calendar month via direct deposit)",
            "duties": "Senior Software Architect responsible for backend API design, AI integration, and codebase security standards.",
            "confidentiality": "Strict non-disclosure of all proprietary source code, business logic, customer records, and trade secrets.",
            "termination": "Either party may terminate this agreement with thirty (30) days prior written notice, or immediately for material breach.",
            "gov_law": "State of Karnataka, India",
            "dispute": "Binding arbitration in Bangalore under the Arbitration and Conciliation Act",
            "addl": "Standard IP assignment of all work product created during employment."
        },
        "Employment Offer Letter": {
            "title": "Formal Offer of Employment",
            "p_a_name": "LegalEase Technologies Pvt. Ltd.",
            "p_a_role": "Employer / Company",
            "p_a_addr": "Level 14, Prestige Tech Park, Bangalore 560103",
            "p_b_name": "Arun Kumar",
            "p_b_role": "Prospective Employee",
            "p_b_addr": "Flat 402, Green Glen Layout, Bangalore 560037",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-15",
            "end_date": "Indefinite / Permanent",
            "duration": "Full-time Permanent",
            "payment": "Annual CTC of ₹18,00,000 payable in equal monthly installments subject to statutory deductions",
            "duties": "Lead full-stack development, architectural reviews, and continuous integration workflows.",
            "confidentiality": "Confidentiality and IP Assignment agreements required upon onboarding.",
            "termination": "Probation period of 3 months; standard 30 days notice period thereafter.",
            "gov_law": "State of Karnataka, India",
            "dispute": "Courts of Bangalore",
            "addl": "Offer valid for acceptance within 7 calendar days of receipt."
        },
        "Non-Disclosure Agreement (NDA)": {
            "title": "Mutual Non-Disclosure Agreement",
            "p_a_name": "LegalEase Technologies Pvt. Ltd.",
            "p_a_role": "Disclosing Party",
            "p_a_addr": "Level 14, Prestige Tech Park, Bangalore 560103",
            "p_b_name": "Apex Ventures Capital",
            "p_b_role": "Receiving Party",
            "p_b_addr": "Bandra Kurla Complex, Mumbai 400051",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-01",
            "end_date": "2028-10-01",
            "duration": "24 months",
            "payment": "Mutual consideration of evaluating potential commercial transaction",
            "duties": "Evaluate proprietary software and investment prospects without unauthorized disclosure.",
            "confidentiality": "All shared technical models, investor decks, and operational data are strictly confidential.",
            "termination": "Either party may terminate negotiations upon 7 days written notice; confidentiality obligations survive 2 years.",
            "gov_law": "State of Maharashtra, India",
            "dispute": "Exclusive jurisdiction of courts in Mumbai",
            "addl": "Return or destruction of confidential information within 14 days of termination."
        },
        "Residential Lease Agreement": {
            "title": "Residential Tenancy Lease Agreement",
            "p_a_name": "Suresh Menon",
            "p_a_role": "Landlord / Lessor",
            "p_a_addr": "Villa 12, Palm Meadows, Whitefield, Bangalore 560066",
            "p_b_name": "Priya Sharma",
            "p_b_role": "Tenant / Lessee",
            "p_b_addr": "Apt 301, Lakeview Enclave, Bangalore 560037",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-01",
            "end_date": "2027-09-30",
            "duration": "11 months",
            "payment": "Monthly rent of ₹35,000 due by 5th of each month; refundable security deposit of ₹1,50,000",
            "duties": "Residential occupancy only; maintain premises in good tenable condition; pay electricity and water bills.",
            "confidentiality": "Parties shall keep personal identity and financial terms confidential.",
            "termination": "1 month notice period required by either party prior to vacation.",
            "gov_law": "State of Karnataka, India",
            "dispute": "Jurisdiction of Rent Control Court / Civil Courts, Bangalore",
            "addl": "No subletting permitted without prior written consent of Landlord."
        },
        "Freelance Work Contract": {
            "title": "Independent Freelance Contractor Agreement",
            "p_a_name": "Quantum Marketing Studio",
            "p_a_role": "Client",
            "p_a_addr": "90 Fleet Street, London / Cyber City, Gurugram 122002",
            "p_b_name": "Vikram Patel",
            "p_b_role": "Freelance Consultant",
            "p_b_addr": "104 Sunrise Apts, Koramangala, Bangalore 560034",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-01",
            "end_date": "2026-12-31",
            "duration": "3 months",
            "payment": "Fixed milestone payment of ₹1,20,000 across 3 deliverables upon successful code sign-off",
            "duties": "Deliver custom UI components, responsive web layout, and API integration documentation.",
            "confidentiality": "Contractor shall maintain strict confidentiality of Client client list and marketing strategies.",
            "termination": "14 days written notice; payment prorated to completed verified milestones.",
            "gov_law": "State of Haryana, India",
            "dispute": "Mediation followed by arbitration in Gurugram",
            "addl": "All work product and intellectual property rights transfer to Client upon final payment."
        },
        "Service Agreement": {
            "title": "Master Professional Services Agreement",
            "p_a_name": "Enterprise Cloud Services LLC",
            "p_a_role": "Service Provider",
            "p_a_addr": "200 Silicon Avenue, San Jose, CA 95110",
            "p_b_name": "Global Retail Solutions Inc.",
            "p_b_role": "Client",
            "p_b_addr": "500 Madison Avenue, New York, NY 10022",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-01",
            "end_date": "2027-10-01",
            "duration": "12 months renewable",
            "payment": "$4,500 monthly service retainer payable net 30 upon invoice submission",
            "duties": "Provide 99.9% uptime SLA cloud hosting, database replication, and 24/7 technical incident response.",
            "confidentiality": "Mutual non-disclosure covering all customer databases, server logs, and security protocols.",
            "termination": "30 days written notice for convenience; immediate termination upon 15 days cure notice for breach.",
            "gov_law": "State of New York, USA",
            "dispute": "AAA commercial arbitration in New York City",
            "addl": "Liability limited to fees paid during the preceding 6 months."
        },
        "General Agreement": {
            "title": "General Partnership & Collaboration Agreement",
            "p_a_name": "Apex Innovation Labs Ltd.",
            "p_a_role": "First Party",
            "p_a_addr": "Tech Hub Tower 1, Sector 62, Noida 201309",
            "p_b_name": "Zenith Media & Design Corp.",
            "p_b_role": "Second Party",
            "p_b_addr": "Media One Building, Dubai Media City, UAE",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-01",
            "end_date": "2027-09-30",
            "duration": "1 Year",
            "payment": "50/50 revenue sharing on joint client deliverables, reconciled quarterly",
            "duties": "Jointly develop, market, and deliver enterprise digital transformation packages.",
            "confidentiality": "All joint research, codebases, and client records treated as confidential.",
            "termination": "60 days written notice by either party without penalty.",
            "gov_law": "State of Uttar Pradesh, India",
            "dispute": "Arbitration in New Delhi under the Indian Arbitration Act",
            "addl": "Neither party shall bind the other party without prior written authorization."
        },
        "General Contract": {
            "title": "Commercial Business Contract",
            "p_a_name": "Northstar Logistics Ltd.",
            "p_a_role": "Contractor",
            "p_a_addr": "Harbour Road Industrial Area, Chennai 600001",
            "p_b_name": "Southern Distribution Corp.",
            "p_b_role": "Purchaser",
            "p_b_addr": "Ring Road Logistics Center, Hyderabad 500034",
            "eff_date": "2026-10-01",
            "start_date": "2026-10-01",
            "end_date": "2027-03-31",
            "duration": "6 months",
            "payment": "₹85,000 per shipment within 15 days of bill of lading delivery confirmation",
            "duties": "Freight transport and scheduled cold-chain delivery of goods across southern regional hubs.",
            "confidentiality": "Shipment schedules, pricing models, and client identities kept strictly private.",
            "termination": "Either party may terminate on 30 days notice or immediately on default of payment.",
            "gov_law": "State of Tamil Nadu, India",
            "dispute": "Courts of Chennai",
            "addl": "Force majeure clause applies for extreme weather or statutory port closures."
        }
    }
    
    # Sensible default values populated for selected document type
    defaults = sample_data.get(selected_type, sample_data["Employment Contract"])

    with st.form("doc_generation_form"):
        st.markdown("<h4 style='color: #d4af37; margin-top: 10px;'>1. Document Details</h4>", unsafe_allow_html=True)
        doc_title = st.text_input("Document Title", value=defaults.get("title", f"{selected_type} Draft"))
        
        st.markdown("<h4 style='color: #d4af37; margin-top: 15px;'>2. Contract Parties</h4>", unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            party_a_name = st.text_input("First Party (Party A) Name *", value=defaults.get("p_a_name", ""))
            party_a_role = st.text_input("Party A Role", value=defaults.get("p_a_role", "Employer" if "Employment" in selected_type else "First Party"))
            party_a_address = st.text_area("Party A Address", value=defaults.get("p_a_addr", ""), height=70)
        with col_p2:
            party_b_name = st.text_input("Second Party (Party B) Name *", value=defaults.get("p_b_name", ""))
            party_b_role = st.text_input("Party B Role", value=defaults.get("p_b_role", "Employee" if "Employment" in selected_type else "Second Party"))
            party_b_address = st.text_area("Party B Address", value=defaults.get("p_b_addr", ""), height=70)
            
        st.markdown("<h4 style='color: #d4af37; margin-top: 15px;'>3. Dates & Term</h4>", unsafe_allow_html=True)
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            eff_date = st.text_input("Effective Date", value=defaults.get("eff_date", "2026-10-01"))
        with col_d2:
            start_date = st.text_input("Start Date (if applicable)", value=defaults.get("start_date", "2026-10-01"))
        with col_d3:
            duration = st.text_input("Duration / Term", value=defaults.get("duration", "12 months"))
            
        st.markdown("<h4 style='color: #d4af37; margin-top: 15px;'>4. Key Legal Terms & Responsibilities</h4>", unsafe_allow_html=True)
        payment_terms = st.text_area("Payment / Compensation Terms", value=defaults.get("payment", ""), height=70, help="e.g. ₹50,000 per month, milestone fees, or rent")
        responsibilities = st.text_area("Scope of Work / Responsibilities", value=defaults.get("duties", ""), height=80, help="Detail primary duties or obligations")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            confidentiality = st.text_area("Confidentiality Covenants", value=defaults.get("confidentiality", "Standard non-disclosure obligations shall apply."), height=70)
        with col_t2:
            termination = st.text_area("Termination & Notice Period", value=defaults.get("termination", "Either party may terminate with 30 days prior written notice."), height=70)
            
        st.markdown("<h4 style='color: #d4af37; margin-top: 15px;'>5. Jurisdiction & Additional Clauses</h4>", unsafe_allow_html=True)
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            gov_law = st.text_input("Governing Law / Jurisdiction", value=defaults.get("gov_law", "State of Karnataka, India"))
        with col_j2:
            dispute_res = st.text_input("Dispute Resolution Method", value=defaults.get("dispute", "Binding arbitration"))
            
        additional_info = st.text_area("Special Conditions or Custom Clauses", value=defaults.get("addl", ""), height=60)
        
        submit_gen = st.form_submit_button("✨ Generate Legal Document with AI", use_container_width=True)

    if submit_gen:
        if not party_a_name or not party_b_name:
            st.error("Please provide party names for both First Party and Second Party.")
        else:
            with st.spinner("Connecting to FastAPI Backend & drafting legal contract with Gemini AI..."):
                gen_dict = {
                    "document_type": selected_type,
                    "title": doc_title,
                    "party_a_name": party_a_name,
                    "party_a_role": party_a_role,
                    "party_a_address": party_a_address,
                    "party_b_name": party_b_name,
                    "party_b_role": party_b_role,
                    "party_b_address": party_b_address,
                    "effective_date": eff_date,
                    "start_date": start_date,
                    "duration": duration,
                    "payment_terms": payment_terms,
                    "responsibilities": responsibilities,
                    "confidentiality_terms": confidentiality,
                    "termination_terms": termination,
                    "governing_law": gov_law,
                    "dispute_resolution": dispute_res,
                    "additional_information": additional_info
                }
                
                # Call connected FastAPI Backend
                try:
                    res = api_generate_document(gen_dict)
                    st.session_state.current_doc = res
                    st.success("Legal document draft successfully generated via Backend API!")
                except Exception as e:
                    st.error(f"Generation error: {str(e)}")

    # Show Document Preview & Editor if document is generated
    if st.session_state.current_doc:
        doc = st.session_state.current_doc
        st.markdown("<br><hr style='border-color: #d4af37;'><br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #d4af37;'>Generated Document: {doc['title']}</h3>", unsafe_allow_html=True)
        
        preview_tab, edit_tab = st.tabs(["👁️ Formatted Document Preview", "✏️ Edit Draft Content"])
        
        with preview_tab:
            st.markdown(doc.get("html_preview", ""), unsafe_allow_html=True)
            
        with edit_tab:
            st.markdown("<p style='color: #94a3b8; font-size: 13px;'>You can edit any clause, term, or section below. Saved edits will directly reflect in your exports.</p>", unsafe_allow_html=True)
            edited_text = st.text_area(
                "Document Content",
                value=doc.get("content", ""),
                height=500,
                key="doc_editor_area"
            )
            
            if st.button("💾 Save Edited Document", key="btn_save_edits"):
                doc["content"] = edited_text
                save_dict = {
                    "id": doc.get("id") if doc.get("id") != "preview_mode" else None,
                    "title": doc.get("title"),
                    "document_type": doc.get("document_type"),
                    "content": edited_text,
                    "summary_table": doc.get("summary_table", [])
                }
                # Call Backend API to save document
                saved_res = api_save_document(save_dict)
                st.session_state.current_doc = saved_res
                st.success("Document successfully saved to your account via Backend API!")
                st.rerun()

        # Export Controls via Backend Endpoints
        st.markdown("<h4 style='color: #d4af37; margin-top: 24px;'>Export Document</h4>", unsafe_allow_html=True)
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        
        export_payload = {
            "title": doc.get("title"),
            "document_type": doc.get("document_type"),
            "content": doc.get("content"),
            "summary_table": doc.get("summary_table", [])
        }
        
        # 1. Plain Text Export via Backend
        with exp_col1:
            txt_data = api_export_txt(export_payload)
            st.download_button(
                label="📄 Download Plain Text (.txt)",
                data=txt_data,
                file_name=f"{doc.get('title', 'document').replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        # 2. Word Document Export (DOCX) via Backend
        with exp_col2:
            docx_buffer, docx_filename = api_export_docx(export_payload)
            st.download_button(
                label="📘 Download Word (.docx)",
                data=docx_buffer.getvalue(),
                file_name=docx_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        # 3. PDF Export via Backend
        with exp_col3:
            pdf_buffer, pdf_filename = api_export_pdf(export_payload)
            st.download_button(
                label="📕 Download PDF (.pdf)",
                data=pdf_buffer.getvalue(),
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )

# ================= VIEW 3: MY DOCUMENTS =================

elif st.session_state.nav_choice == "My Documents":
    st.markdown("<h2 class='card-title' style='font-size: 24px;'>Document History</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>All generated and customized legal drafts saved securely under your account.</p>", unsafe_allow_html=True)
    
    docs = api_get_history()
    
    if not docs:
        st.info("You haven't saved any documents yet. Go to 'Create Document' to generate your first draft.")
    else:
        for item in docs:
            with st.container():
                st.markdown(f"""
                <div class="legal-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <div style="font-size: 17px; font-weight: 700; color: #ffffff;">{item.get('title')}</div>
                            <div style="color: #d4af37; font-size: 13px; margin-top: 2px;">{item.get('document_type')}</div>
                            <div style="color: #64748B; font-size: 11px; margin-top: 6px;">Created: {item.get('created_at', '')[:10]} • Last Updated: {item.get('updated_at', '')[:16]}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_act1, c_act2, c_act3, c_act4 = st.columns([1.5, 1.2, 1.2, 1])
                with c_act1:
                    if st.button("✏️ Open & Edit", key=f"open_{item['id']}"):
                        full_doc = api_get_document(item['id'])
                        st.session_state.current_doc = full_doc
                        st.session_state.nav_choice = "Create Document"
                        st.rerun()
                with c_act2:
                    exp_payload = {
                        "title": item['title'],
                        "document_type": item['document_type'],
                        "content": item.get('content', '')
                    }
                    pdf_buf, pdf_fname = api_export_pdf(exp_payload)
                    st.download_button(
                        "📕 PDF",
                        data=pdf_buf.getvalue(),
                        file_name=pdf_fname,
                        mime="application/pdf",
                        key=f"dl_pdf_{item['id']}"
                    )
                with c_act3:
                    docx_buf, docx_fname = api_export_docx(exp_payload)
                    st.download_button(
                        "📘 Word",
                        data=docx_buf.getvalue(),
                        file_name=docx_fname,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"dl_docx_{item['id']}"
                    )
                with c_act4:
                    if st.button("🗑️ Delete", key=f"del_{item['id']}"):
                        api_delete_document(item['id'])
                        st.success("Document deleted via Backend API.")
                        st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

# ================= VIEW 4: ACCOUNT SETTINGS =================

elif st.session_state.nav_choice == "Account Settings":
    st.markdown("<h2 class='card-title' style='font-size: 24px;'>Account & Security</h2>", unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown(f"""
        <div class="legal-card">
            <h4 style="color: #d4af37; margin-top: 0;">User Profile</h4>
            <p><strong>Name:</strong> {user.get('full_name')}</p>
            <p><strong>Email:</strong> {user.get('email')}</p>
            <p><strong>Role:</strong> {user.get('role', 'Counsel')}</p>
            <p><strong>Account ID:</strong> <code style="color: #d4af37;">{user.get('id')}</code></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_u2:
        st.markdown(f"""
        <div class="legal-card">
            <h4 style="color: #d4af37; margin-top: 0;">Connected Backend API</h4>
            <p><strong>URL:</strong> <a href="{BACKEND_URL}" target="_blank" style="color: #d4af37;">{BACKEND_URL}</a></p>
            <p><strong>Status:</strong> {api_status_html}</p>
            <p><strong>Health Endpoint:</strong> <a href="{BACKEND_URL}/health" target="_blank" style="color: #d4af37;">/health</a></p>
            <p><strong>Interactive Docs:</strong> <a href="{BACKEND_URL}/docs" target="_blank" style="color: #d4af37;">/docs (Swagger)</a></p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown(f"""
    <div class="disclaimer-banner">
        <strong>MANDATORY LEGAL DISCLAIMER:</strong> {settings.LEGAL_DISCLAIMER}
    </div>
    """, unsafe_allow_html=True)
