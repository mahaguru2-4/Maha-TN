import pytest
from pydantic import ValidationError
from backend.models import DocumentGenerateRequest
from backend.utils.sanitizer import sanitize_text, clean_filename
from backend.services.storage_service import storage_service

def test_sanitizer():
    dirty_text = "Party A’s agreement \x00with Party B “quoted” — special.\r\n\r\n\r\nNext line."
    clean = sanitize_text(dirty_text)
    assert "\x00" not in clean
    assert "Party A's agreement with Party B \"quoted\" -- special." in clean
    assert "\r" not in clean

def test_clean_filename():
    assert clean_filename("Employment Contract / 2026: Edition") == "Employment_Contract__2026_Edition"
    assert clean_filename("") == "document"

def test_validation_missing_parties():
    # party_a_name and party_b_name are required
    with pytest.raises(ValidationError):
        DocumentGenerateRequest(
            document_type="Employment Contract",
            party_a_name="",
            party_b_name="Someone"
        )
    with pytest.raises(ValidationError):
        DocumentGenerateRequest(
            document_type="Employment Contract",
            party_a_name="Employer",
            party_b_name=""
        )

def test_user_isolation():
    # User 1 creates document
    doc1 = storage_service.save_document(
        user_id="user-alpha-123",
        title="Alpha Confidential",
        document_type="NDA",
        content="Secret alpha content"
    )
    # User 2 creates document
    doc2 = storage_service.save_document(
        user_id="user-beta-456",
        title="Beta Lease",
        document_type="Residential Lease Agreement",
        content="Beta rent terms"
    )
    
    # User 1 attempts to fetch User 2's document -> must be None
    assert storage_service.get_document_by_id(doc2["id"], user_id="user-alpha-123") is None
    
    # User 2 attempts to fetch User 1's document -> must be None
    assert storage_service.get_document_by_id(doc1["id"], user_id="user-beta-456") is None
    
    # User 1 history must only contain Alpha
    u1_docs = storage_service.get_user_documents(user_id="user-alpha-123")
    assert any(d["id"] == doc1["id"] for d in u1_docs)
    assert not any(d["id"] == doc2["id"] for d in u1_docs)
