from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import os
from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    SCOPES,
)
from database import save_credentials, load_credentials, delete_credentials, get_all_users

# Allow scope changes (Google adds 'openid' automatically)
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

# In-memory cache (loaded from DB on startup)
credentials_store = {}

def get_credentials():
    """Get credentials from cache or database"""
    # Check memory cache first
    if "credentials" in credentials_store:
        creds = credentials_store["credentials"]
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(creds)
            credentials_store["credentials"] = creds
        return creds
    
    # Try loading from database
    creds = load_credentials()
    if creds:
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_credentials(creds)
        credentials_store["credentials"] = creds
        return creds
    
    return None

router = APIRouter()

@router.get("/login")
def login(redirect: bool = True, force: bool = False):
    """
    Start Google OAuth login.
    - Automatically skips login if already authenticated (unless force=True)
    - If redirect=True (default): Automatically redirects to Google login
    - If redirect=False: Returns the auth URL as JSON
    - If force=True: Forces re-authentication even if already logged in
    """
    # Check if already authenticated
    if not force:
        creds = get_credentials()
        if creds and not creds.expired:
            if redirect:
                return RedirectResponse(url="/auth/success")
            return {
                "message": "Already authenticated!",
                "authenticated": True,
                "hint": "Use /auth/login?force=true to re-authenticate"
            }
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )

    flow.redirect_uri = GOOGLE_REDIRECT_URI

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    if redirect:
        return RedirectResponse(url=auth_url)
    
    return {"auth_url": auth_url}


@router.get("/callback")
def callback(code: str):
    """
    OAuth callback - Google redirects here with authorization code
    """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )

    flow.redirect_uri = GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)

    credentials = flow.credentials
    
    # Store in memory cache
    credentials_store["credentials"] = credentials
    
    # Persist to SQLite database
    save_credentials(credentials)

    # Redirect to success page
    return RedirectResponse(url="http://localhost:5173")


@router.get("/success")
def auth_success():
    """Success page after authentication"""
    creds = get_credentials()
    if creds:
        return {
            "message": "✅ Authentication successful!",
            "status": "logged_in",
            "session_persisted": True,
            "token_expiry": str(creds.expiry) if creds.expiry else None,
            "hint": "Your session is saved. You won't need to login again even after server restart!"
        }
    return {"message": "Not authenticated", "status": "logged_out"}


@router.get("/status")
def auth_status():
    """Check if user is authenticated"""
    creds = get_credentials()
    if creds:
        return {
            "authenticated": True,
            "expired": creds.expired,
            "expiry": str(creds.expiry) if creds.expiry else None,
        }
    return {"authenticated": False}


@router.post("/logout")
def logout():
    """Clear stored credentials"""
    credentials_store.clear()
    delete_credentials()
    return {"message": "Logged out successfully"}


