"""
Database module for storing OAuth credentials
Uses MongoDB Atlas for persistence (serverless-friendly)
Version: 2.0 - Vercel serverless compatible
"""
import os
import json
from datetime import datetime
from typing import Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# MongoDB Atlas connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "google_services")

# Global client (connection pooling)
_client = None
_db = None


def get_database():
    """Get MongoDB database connection with connection pooling"""
    global _client, _db
    
    if _db is not None:
        return _db
    
    try:
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
        # Test connection
        _client.admin.command('ping')
        _db = _client[DATABASE_NAME]
        print("✅ Connected to MongoDB Atlas")
        return _db
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise


def init_db():
    """Initialize the MongoDB database and collections"""
    try:
        db = get_database()
        # Create collection if not exists
        if "oauth_tokens" not in db.list_collection_names():
            db.create_collection("oauth_tokens")
        
        # Create index on user_email for faster lookups
        db.oauth_tokens.create_index("user_email", unique=True)
        print("✅ MongoDB initialized successfully")
    except Exception as e:
        print(f"⚠️ MongoDB init warning: {e}")


def save_credentials(credentials: Any, user_email: str = "default"):
    """Save OAuth credentials to MongoDB"""
    ensure_initialized()
    try:
        db = get_database()
        
        scopes_list = list(credentials.scopes) if credentials.scopes else []
        expiry_str = credentials.expiry.isoformat() if credentials.expiry else None
        
        document = {
            "user_email": user_email,
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": scopes_list,
            "expiry": expiry_str,
            "updated_at": datetime.now().isoformat()
        }
        
        # Upsert - insert or update if exists
        db.oauth_tokens.update_one(
            {"user_email": user_email},
            {"$set": document, "$setOnInsert": {"created_at": datetime.now().isoformat()}},
            upsert=True
        )
        print(f"✅ Credentials saved for {user_email}")
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        raise


def load_credentials(user_email: str = "default") -> Any:
    """Load OAuth credentials from MongoDB"""
    from google.oauth2.credentials import Credentials
    ensure_initialized()
    try:
        db = get_database()
        
        document = db.oauth_tokens.find_one({"user_email": user_email})
        
        if not document:
            return None
        
        expiry = datetime.fromisoformat(document["expiry"]) if document.get("expiry") else None
        
        credentials = Credentials(
            token=document["token"],
            refresh_token=document.get("refresh_token"),
            token_uri=document.get("token_uri"),
            client_id=document.get("client_id"),
            client_secret=document.get("client_secret"),
            scopes=document.get("scopes"),
        )
        credentials.expiry = expiry
        
        return credentials
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return None


def delete_credentials(user_email: str = "default"):
    """Delete OAuth credentials from MongoDB"""
    ensure_initialized()
    try:
        db = get_database()
        db.oauth_tokens.delete_one({"user_email": user_email})
        print(f"✅ Credentials deleted for {user_email}")
    except Exception as e:
        print(f"❌ Error deleting credentials: {e}")
        raise


def get_all_users():
    """Get all users with stored credentials"""
    ensure_initialized()
    try:
        db = get_database()
        cursor = db.oauth_tokens.find(
            {},
            {"user_email": 1, "created_at": 1, "updated_at": 1}
        )
        return [
            {
                "email": doc.get("user_email"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at")
            }
            for doc in cursor
        ]
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return []


# Lazy initialization for serverless - don't call init_db() at import time
# Database will be initialized on first actual database operation
_initialized = False


def ensure_initialized():
    """Ensure database is initialized (called lazily on first operation)"""
    global _initialized
    if not _initialized:
        try:
            init_db()
            _initialized = True
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
