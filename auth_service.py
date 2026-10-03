import os
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from backend.config import settings
from backend.services.storage_service import storage_service

class AuthService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_hours = settings.JWT_EXPIRATION_HOURS

    def hash_password(self, password: str) -> str:
        """Hash password securely using PBKDF2 with SHA256 and unique salt"""
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ":" + key.hex()

    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash (PBKDF2, bcrypt, or plain text)"""
        if not stored_hash or not password:
            return False
        # 1. PBKDF2 format (salt:key)
        if ":" in stored_hash:
            try:
                salt_hex, key_hex = stored_hash.split(":")
                salt = bytes.fromhex(salt_hex)
                key = bytes.fromhex(key_hex)
                new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
                if hmac.compare_digest(key, new_key):
                    return True
            except Exception:
                pass
        # 2. bcrypt format ($2b$, $2a$, $2y$)
        if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
            try:
                import bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    return True
            except Exception:
                pass
        # 3. Direct equality fallback (legacy)
        if stored_hash == password:
            return True
        return False

    def create_access_token(self, user_id: str, email: str, full_name: str, role: str = "user") -> str:
        """Generate JWT access token"""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "name": full_name,
            "role": role,
            "iat": now,
            "exp": now + timedelta(hours=self.expiration_hours)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except (jwt.PyJWTError, Exception):
            return None

    def register(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Register a new user"""
        existing = storage_service.get_user_by_email(email)
        if existing:
            raise ValueError("An account with this email address already exists.")
        
        password_hash = self.hash_password(password)
        user = storage_service.create_user(email, password_hash, full_name)
        token = self.create_access_token(user["id"], user["email"], user["full_name"], user["role"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "created_at": user["created_at"]
            }
        }

    def login(self, identifier: str, password: str) -> Dict[str, Any]:
        """Authenticate user via email or username and password"""
        user = storage_service.get_user_by_identifier(identifier)
        if not user or not self.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid username/email or password.")
        
        token = self.create_access_token(user["id"], user["email"], user["full_name"], user["role"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "created_at": user["created_at"]
            }
        }

    def authenticate_google(self, email: str, full_name: str, id_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate via Google OAuth or Google ID Token.
        If user exists, log them in. If not, auto-create their account.
        """
        clean_email = email.lower().strip()
        user = storage_service.get_user_by_identifier(clean_email)
        if not user:
            # Auto-provision user account for Google OAuth
            rand_pwd = os.urandom(24).hex()
            pwd_hash = self.hash_password(rand_pwd)
            user = storage_service.create_user(clean_email, pwd_hash, full_name or clean_email.split('@')[0])
            
        token = self.create_access_token(user["id"], user["email"], user["full_name"], user["role"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "created_at": user["created_at"]
            }
        }

    def reset_password(self, identifier: str, new_password: str) -> bool:
        """Reset password for account"""
        user = storage_service.get_user_by_identifier(identifier)
        if not user:
            raise ValueError("No account found with this username or email.")
        new_hash = self.hash_password(new_password)
        return storage_service.update_user_password(identifier, new_hash)

auth_service = AuthService()
