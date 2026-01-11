"""
Shared dependencies for authentication across all routes
"""
from fastapi import Cookie, HTTPException, Depends
from typing import Optional

SESSION_COOKIE_NAME = "session_id"


def get_session_id(session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)) -> Optional[str]:
    """Get session ID from cookie"""
    return session_id


def require_session(session_id: Optional[str] = Depends(get_session_id)) -> str:
    """Require a valid session ID, raise 401 if not present"""
    if not session_id:
        raise HTTPException(
            status_code=401, 
            detail="Not authenticated. Please login first at /auth/login"
        )
    return session_id
