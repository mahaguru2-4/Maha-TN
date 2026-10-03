import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from backend.config import settings

class StorageService:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT NOT NULL
                )
            """)
            
            # Documents table (Strictly user-isolated by user_id)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    summary_table TEXT NOT NULL DEFAULT '[]',
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Indexes for quick user lookup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_user_id ON documents(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            conn.commit()

    # User Management
    def create_user(self, email: str, password_hash: str, full_name: str, role: str = "user") -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO users (id, email, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, email.lower().strip(), password_hash, full_name.strip(), role, created_at)
            )
            conn.commit()
        return {
            "id": user_id,
            "email": email.lower().strip(),
            "full_name": full_name.strip(),
            "role": role,
            "created_at": created_at
        }

    def get_user_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        clean_id = identifier.lower().strip()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE LOWER(email) = ? OR LOWER(full_name) = ?",
                (clean_id, clean_id)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.get_user_by_identifier(email)

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_user_password(self, identifier: str, new_password_hash: str) -> bool:
        clean_id = identifier.lower().strip()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE users SET password_hash = ? WHERE LOWER(email) = ? OR LOWER(full_name) = ?",
                (new_password_hash, clean_id, clean_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    # User-Isolated Document Management
    def save_document(
        self,
        user_id: str,
        title: str,
        document_type: str,
        content: str,
        summary_table: Optional[List[Dict[str, str]]] = None,
        doc_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        table_json = json.dumps(summary_table or [])
        meta_json = json.dumps(metadata or {})
        
        with self._get_connection() as conn:
            if doc_id:
                # Check ownership: only update if document belongs to this user_id
                cursor = conn.execute("SELECT id FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
                if cursor.fetchone():
                    conn.execute("""
                        UPDATE documents 
                        SET title = ?, document_type = ?, content = ?, summary_table = ?, metadata = ?, updated_at = ?
                        WHERE id = ? AND user_id = ?
                    """, (title, document_type, content, table_json, meta_json, now, doc_id, user_id))
                    conn.commit()
                    return {
                        "id": doc_id,
                        "user_id": user_id,
                        "title": title,
                        "document_type": document_type,
                        "content": content,
                        "summary_table": summary_table or [],
                        "metadata": metadata or {},
                        "updated_at": now
                    }
            
            # Create new document
            new_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO documents (id, user_id, title, document_type, content, summary_table, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_id, user_id, title, document_type, content, table_json, meta_json, now, now))
            conn.commit()
            return {
                "id": new_id,
                "user_id": user_id,
                "title": title,
                "document_type": document_type,
                "content": content,
                "summary_table": summary_table or [],
                "metadata": metadata or {},
                "created_at": now,
                "updated_at": now
            }

    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch all documents for a specific user only, sorted by updated_at descending"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, document_type, created_at, updated_at, summary_table, metadata FROM documents WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                doc = dict(r)
                doc["summary_table"] = json.loads(doc.get("summary_table", "[]"))
                doc["metadata"] = json.loads(doc.get("metadata", "{}"))
                results.append(doc)
            return results

    def get_document_by_id(self, doc_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific document, enforcing user ownership"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM documents WHERE id = ? AND user_id = ?",
                (doc_id, user_id)
            )
            row = cursor.fetchone()
            if row:
                doc = dict(row)
                doc["summary_table"] = json.loads(doc.get("summary_table", "[]"))
                doc["metadata"] = json.loads(doc.get("metadata", "{}"))
                return doc
            return None

    def delete_document(self, doc_id: str, user_id: str) -> bool:
        """Delete document belonging to specific user"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM documents WHERE id = ? AND user_id = ?", (doc_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

storage_service = StorageService()
