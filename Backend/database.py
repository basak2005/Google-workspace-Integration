"""
Database module for storing OAuth credentials
Uses SQLite for persistence across server restarts
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Any

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "tokens.db")


def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id INTEGER PRIMARY KEY,
            user_email TEXT UNIQUE,
            token TEXT NOT NULL,
            refresh_token TEXT,
            token_uri TEXT,
            client_id TEXT,
            client_secret TEXT,
            scopes TEXT,
            expiry TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_credentials(credentials: Any, user_email: str = "default"):
    """Save OAuth credentials to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    scopes_json = json.dumps(list(credentials.scopes)) if credentials.scopes else "[]"
    expiry_str = credentials.expiry.isoformat() if credentials.expiry else None
    
    cursor.execute("""
        INSERT OR REPLACE INTO oauth_tokens 
        (user_email, token, refresh_token, token_uri, client_id, client_secret, scopes, expiry, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_email,
        credentials.token,
        credentials.refresh_token,
        credentials.token_uri,
        credentials.client_id,
        credentials.client_secret,
        scopes_json,
        expiry_str,
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()


def load_credentials(user_email: str = "default") -> Any:
    """Load OAuth credentials from database"""
    from google.oauth2.credentials import Credentials
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT token, refresh_token, token_uri, client_id, client_secret, scopes, expiry
        FROM oauth_tokens WHERE user_email = ?
    """, (user_email,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    token, refresh_token, token_uri, client_id, client_secret, scopes_json, expiry_str = row
    
    scopes = json.loads(scopes_json) if scopes_json else None
    expiry = datetime.fromisoformat(expiry_str) if expiry_str else None
    
    credentials = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )
    credentials.expiry = expiry
    
    return credentials


def delete_credentials(user_email: str = "default"):
    """Delete OAuth credentials from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM oauth_tokens WHERE user_email = ?", (user_email,))
    conn.commit()
    conn.close()


def get_all_users():
    """Get all users with stored credentials"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_email, created_at, updated_at FROM oauth_tokens")
    rows = cursor.fetchall()
    conn.close()
    return [{"email": r[0], "created_at": r[1], "updated_at": r[2]} for r in rows]


# Initialize database on module import
init_db()
