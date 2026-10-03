# LegalEase — AI-Powered Legal Document Generator

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.8_Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org)
[![Theme](https://img.shields.io/badge/Theme-Dark_Navy_%2B_Gold-D4AF37.svg)](#visual-theme)

> **Enterprise-grade, AI-assisted legal contract and agreement generator engineered with Google Gemini, FastAPI, and Streamlit.**

---

## ⚖️ Live Public Deployment URLs

- **Public Frontend Application (Streamlit)**: [https://supplements-spa-which-independent.trycloudflare.com](https://supplements-spa-which-independent.trycloudflare.com)
- **Public Backend API (FastAPI)**: [https://lincoln-quite-ratio-speech.trycloudflare.com](https://lincoln-quite-ratio-speech.trycloudflare.com)
- **Public Health Check**: [https://lincoln-quite-ratio-speech.trycloudflare.com/health](https://lincoln-quite-ratio-speech.trycloudflare.com/health)
- **Interactive Swagger API Documentation**: [https://lincoln-quite-ratio-speech.trycloudflare.com/docs](https://lincoln-quite-ratio-speech.trycloudflare.com/docs)

---

## 🌟 Executive Summary & Purpose

**LegalEase** empowers businesses, legal practitioners, consultants, and individuals to quickly generate customizable, professionally formatted legal drafts across 8 critical contract categories:

1. **Employment Contract**
2. **Employment Offer Letter**
3. **Non-Disclosure Agreement (NDA)**
4. **Residential Lease Agreement**
5. **Freelance Work Contract**
6. **Service Agreement**
7. **General Agreement**
8. **General Contract**

### Key Capabilities
- **AI-Powered Legal Drafting**: Uses Google Gemini (`gemini-3.8-flash`) via the modern `google-genai` SDK with strict legal guardrails against hallucinating names, dates, financial sums, or statutory citations.
- **Deterministic Legal Fallback Engine**: If Gemini credentials are not supplied or network interruptions occur, the internal deterministic legal drafting rules engine automatically takes over, ensuring 100% operational uptime.
- **Editable In-Browser Preview**: Dual-mode preview with formatted HTML viewer and rich interactive text editor allowing modifications before export.
- **Multi-Format Export Engine**:
  - **Adobe PDF (`.pdf`)**: Vector branding, executive terms table, numbered legal clauses, signature blocks, running header/footer with page numbers.
  - **Microsoft Word (`.docx`)**: 1-inch standard legal margins, custom table borders, gold accents, and Times New Roman typography.
  - **Plain Text (`.txt`)**: Clean ASCII text format preserving all user modifications.
- **Enterprise Security & Isolation**: User-specific document isolation backed by SQLite with write-ahead logging (WAL), PBKDF2/bcrypt salted password hashing, and JWT authorization.
- **Responsive Dark Navy + Gold Visual Theme**: Modern, high-contrast, premium interface built for desktop, tablet, and mobile screens.

---

## 🏛️ System Architecture

```
                                      USER
                                        │
                                        ▼
                             PUBLIC HTTPS CLOUDFLARE
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
        STREAMLIT FRONTEND (8501)               FASTAPI BACKEND (8000)
    (Dark Navy + Gold SaaS Portal)              (RESTful Microservices)
                    │                                       │
                    ├───────────────────────────────────────┤
                    ▼                                       ▼
        AUTHENTICATION SERVICE                     GEMINI AI ENGINE
       (JWT / PBKDF2 / OAuth)                  (google-genai / Gemini 3.8)
                    │                                       │
                    ▼                                       ▼
          ISOLATED DATABASE                         DOCUMENT ENGINE
        (Per-user SQLite WAL)                   (python-docx / ReportLab)
                                                            │
                                                ┌───────────┼───────────┐
                                                ▼           ▼           ▼
                                               TXT         DOCX        PDF
```

---

## 🛡️ AI Safety & Anti-Hallucination Guardrails

LegalEase implements strict server-side rules in `backend/ai_core/gemini_generator.py`:
- **No Fabricated Facts**: Gemini is strictly prohibited from inventing entity names, physical addresses, dates, compensation sums, or durations.
- **Missing Information Placeholders**: Any omitted parameter is conspicuously tagged in uppercase brackets (e.g. `[INSERT EMPLOYER ADDRESS]`, `[DATE REQUIRED]`, `[COMPENSATION AMOUNT TO BE SPECIFIED]`).
- **No False Legal Authority**: The model never fabricates jurisdiction statutes or fictitious court citations.
- **Mandatory Legal Disclaimer**: Every generated document and application view incorporates a clear legal disclaimer advising users that drafts must be reviewed by qualified legal counsel.

---

## 🎨 Visual Theme — Dark Navy + Gold

The UI implements a high-end legal-tech design language:
- **Deep Navy Background**: `#070D1D` and `#0A1128`
- **Gold Accents**: `#D4AF37`, `#F3C68F`, `#E5C158`
- **Surface Elevation Cards**: `#0D152B` with `#1E2C4F` subtle borders
- **Typography**: Cinzel serif for brand titles, Inter sans-serif for UI, Times New Roman for contract clauses.

---

## 📂 Project Directory Structure

```
c:\modernlegaldocument\
│
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint & middleware
│   ├── routes.py                # REST endpoints (auth, generate, save, history, export)
│   ├── models.py                # Pydantic schemas and document validation models
│   ├── config.py                # Configuration and environment settings
│   │
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py  # Google Gemini SDK & deterministic legal fallback
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # PBKDF2/bcrypt hashing, JWT tokens, Google OAuth
│   │   ├── document_service.py  # Generation, persistence, and export pipeline
│   │   └── storage_service.py   # Thread-safe SQLite repository with user isolation
│   │
│   └── utils/
│       ├── __init__.py
│       ├── sanitizer.py         # Input text, HTML escaping, and filename sanitization
│       ├── docx_formatter.py    # python-docx legal generator (tables, headers, footers)
│       ├── pdf_formatter.py     # ReportLab PDF generator with running canvas & pagination
│       └── html_formatter.py    # Responsive HTML preview formatter
│
├── frontend/
│   ├── __init__.py
│   ├── app.py                   # Streamlit multi-page dashboard & document generator
│   └── styles.py                # Dark Navy + Gold CSS stylesheet
│
├── assets/
│   └── logo/
│       ├── legalease_logo.png   # Full horizontal banner logo
│       └── legalease_emblem.png # Scales of Justice shield emblem
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py              # Automated FastAPI integration tests
│   ├── test_documents.py        # DOCX, PDF, and TXT generation tests
│   └── test_validation.py       # Pydantic validation & user isolation tests
│
├── scripts/
│   ├── create_logo.py           # Brand asset generation script
│   └── test_e2e_live.py         # Live E2E verification against deployed HTTPS URLs
│
├── .env.example                 # Configuration template with security placeholders
├── requirements.txt             # Production Python dependencies
├── run_backend.py               # Backend startup script
├── run_frontend.py              # Frontend startup script
└── README.md                    # System documentation
```

---

## ⚙️ Installation & Local Setup

### 1. Prerequisites
- Python 3.11+
- pip

### 2. Clone / Open Project
```bash
cd c:\modernlegaldocument
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Set your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=8000
BACKEND_URL=https://lincoln-quite-ratio-speech.trycloudflare.com
```

---

## 🚀 Running the Application

### 1. Launch FastAPI Backend
```bash
python run_backend.py
```
Backend will start on `http://0.0.0.0:8000` with interactive Swagger docs at `/docs`.

### 2. Launch Streamlit Frontend
```bash
streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0
```
Frontend will be accessible at `http://localhost:8501`.

---

## 🧪 Testing Suite

LegalEase includes comprehensive unit, integration, and live end-to-end tests.

### Run Automated Tests
```bash
python -m pytest tests/ -v
```
All 13 automated tests verify:
- Root & `/health` endpoints
- User registration, login, and JWT decoding
- Contract generation with terms table
- DOCX, PDF, TXT exports
- Text sanitization against control characters and XSS
- Strict user data isolation

### Run Live End-to-End Test on Deployed Public HTTPS API
```bash
python scripts/test_e2e_live.py
```
Executes 12 live network verification steps against the public HTTPS deployment.

---

## 🌐 Public HTTPS Deployment

The application is deployed publicly via Cloudflare Quick Tunnels:

| Component | Public URL | Description |
|-----------|------------|-------------|
| **Frontend Portal** | `https://supplements-spa-which-independent.trycloudflare.com` | Streamlit SaaS UI |
| **Backend REST API** | `https://lincoln-quite-ratio-speech.trycloudflare.com` | FastAPI Service |
| **Health Check** | `https://lincoln-quite-ratio-speech.trycloudflare.com/health` | Deployment Monitoring |
| **API Docs (Swagger)** | `https://lincoln-quite-ratio-speech.trycloudflare.com/docs` | OpenAPI Specification |

---

## 🔒 Security & Privacy Notice

- **Server-Side Credentials**: Gemini API keys and JWT signing secrets are stored exclusively server-side and never exposed to client-side code.
- **Password Protection**: Passwords are salted and hashed using PBKDF2 with SHA-256 (100,000 rounds).
- **Data Privacy**: Logs do not store confidential document clauses or private party information.
- **User Isolation**: Database queries strictly filter by authenticated `user_id`.

---

## ⚖️ Legal Disclaimer

> **IMPORTANT**: LegalEase generates AI-assisted legal document drafts for informational and drafting purposes only. It does not provide legal advice and does not guarantee that any document is legally valid, sufficient, enforceable, or suitable for any specific jurisdiction. Users are strongly advised to have all important legal documents reviewed by a qualified legal professional licensed in their jurisdiction prior to execution.
