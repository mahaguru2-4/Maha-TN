from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field, EmailStr

class DocumentType(str, Enum):
    EMPLOYMENT_CONTRACT = "Employment Contract"
    EMPLOYMENT_OFFER_LETTER = "Employment Offer Letter"
    NDA = "Non-Disclosure Agreement (NDA)"
    RESIDENTIAL_LEASE = "Residential Lease Agreement"
    FREELANCE_CONTRACT = "Freelance Work Contract"
    SERVICE_AGREEMENT = "Service Agreement"
    GENERAL_AGREEMENT = "General Agreement"
    GENERAL_CONTRACT = "General Contract"

class TableRow(BaseModel):
    term: str
    details: str

class DocumentGenerateRequest(BaseModel):
    document_type: str = Field(..., description="Type of legal document")
    title: Optional[str] = Field(None, description="Optional custom document title")
    
    # Parties
    party_a_name: str = Field(..., min_length=1, description="First party or employer / landlord / client")
    party_a_role: Optional[str] = Field(None, description="e.g. Employer, Landlord, Disclosing Party")
    party_a_address: Optional[str] = Field(None, description="Address of Party A")
    
    party_b_name: str = Field(..., min_length=1, description="Second party or employee / tenant / contractor")
    party_b_role: Optional[str] = Field(None, description="e.g. Employee, Tenant, Receiving Party")
    party_b_address: Optional[str] = Field(None, description="Address of Party B")
    
    # Dates & Duration
    effective_date: Optional[str] = Field(None, description="Effective Date of agreement")
    start_date: Optional[str] = Field(None, description="Start date of employment, lease, or service")
    end_date: Optional[str] = Field(None, description="End date if fixed term")
    duration: Optional[str] = Field(None, description="e.g. 12 months, Indefinite, 90 days")
    
    # Terms
    payment_terms: Optional[str] = Field(None, description="Salary, rent, consulting fee, payment milestones")
    responsibilities: Optional[str] = Field(None, description="Key duties, job scope, services rendered")
    confidentiality_terms: Optional[str] = Field(None, description="Non-disclosure and proprietary covenants")
    termination_terms: Optional[str] = Field(None, description="Notice period and grounds for termination")
    governing_law: Optional[str] = Field(None, description="Governing state or jurisdiction")
    dispute_resolution: Optional[str] = Field(None, description="Arbitration, mediation, or courts")
    additional_information: Optional[str] = Field(None, description="Special terms, covenants, or clauses")
    
    # Formatting options
    include_terms_table: bool = Field(True, description="Whether to include summary terms table")
    include_signatures: bool = Field(True, description="Whether to include signature blocks")

class DocumentResponse(BaseModel):
    id: str
    document_type: str
    title: str
    content: str
    summary_table: list[dict[str, str]]
    created_at: str
    updated_at: str
    user_id: Optional[str] = None
    disclaimer: str

class DocumentSaveRequest(BaseModel):
    id: Optional[str] = None
    title: str
    document_type: str
    content: str
    summary_table: Optional[list[dict[str, str]]] = []
    metadata: Optional[dict[str, Any]] = {}

class ExportRequest(BaseModel):
    title: str
    document_type: str
    content: str
    summary_table: Optional[list[dict[str, str]]] = []
    effective_date: Optional[str] = None
    party_a_name: Optional[str] = None
    party_b_name: Optional[str] = None

# Authentication Models
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

class UserRegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    username: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    username_or_email: Optional[str] = None
    password: str

    @property
    def identifier(self) -> str:
        return (self.email or self.username or self.username_or_email or "").strip()

class GoogleAuthRequest(BaseModel):
    id_token: Optional[str] = None
    email: str = Field(..., min_length=3)
    full_name: str
    google_id: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    new_password: str = Field(..., min_length=6)

    @property
    def identifier(self) -> str:
        return (self.email or self.username or "").strip()

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    ai_engine: str
    model: str
