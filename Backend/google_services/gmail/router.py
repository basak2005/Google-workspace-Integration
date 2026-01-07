"""
Gmail API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth.router import get_credentials
from google_services.gmail_service import (
    list_messages,
    get_message,
    send_email,
    get_labels,
)

router = APIRouter(prefix="/gmail", tags=["Gmail"])


class EmailSend(BaseModel):
    to: str
    subject: str
    body: str
    html: bool = False


@router.get("/messages")
def get_messages(max_results: int = 10, query: str = ""):
    """
    List emails from inbox.
    Query examples: "is:unread", "from:someone@gmail.com", "subject:hello"
    """
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_messages(credentials, max_results, query)


@router.get("/messages/{message_id}")
def get_email(message_id: str):
    """Get full email content by ID"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_message(credentials, message_id)


@router.post("/send")
def send(email: EmailSend):
    """Send an email"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return send_email(credentials, email.to, email.subject, email.body, email.html)


@router.get("/labels")
def labels():
    """Get all Gmail labels"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_labels(credentials)
