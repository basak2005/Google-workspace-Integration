"""
Gmail Service
Integrates with Gmail API for reading and sending emails
"""
from googleapiclient.discovery import build
from typing import Any
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_gmail_service(credentials: Any):
    """Create Gmail service instance"""
    return build("gmail", "v1", credentials=credentials)


def list_messages(credentials: Any, max_results: int = 10, query: str = ""):
    """
    List emails from inbox
    query examples: "is:unread", "from:example@gmail.com", "subject:hello"
    """
    service = get_gmail_service(credentials)
    
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        q=query
    ).execute()
    
    messages = results.get("messages", [])
    
    # Get details for each message
    detailed_messages = []
    for msg in messages:
        msg_detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()
        
        headers = {h["name"]: h["value"] for h in msg_detail.get("payload", {}).get("headers", [])}
        detailed_messages.append({
            "id": msg["id"],
            "threadId": msg["threadId"],
            "snippet": msg_detail.get("snippet", ""),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
        })
    
    return detailed_messages


def get_message(credentials: Any, message_id: str):
    """Get full email content by ID"""
    service = get_gmail_service(credentials)
    
    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()
    
    headers = {h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])}
    
    # Extract body
    body = ""
    payload = message.get("payload", {})
    
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                body = base64.urlsafe_b64decode(data).decode("utf-8")
                break
    elif "body" in payload and "data" in payload["body"]:
        body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
    
    return {
        "id": message["id"],
        "threadId": message["threadId"],
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "body": body,
        "snippet": message.get("snippet", ""),
    }


def send_email(credentials: Any, to: str, subject: str, body: str, html: bool = False):
    """Send an email"""
    service = get_gmail_service(credentials)
    
    if html:
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(body, "html"))
    else:
        message = MIMEText(body)
    
    message["to"] = to
    message["subject"] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    
    result = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
    
    return {"message_id": result["id"], "status": "sent"}


def get_labels(credentials: Any):
    """Get all Gmail labels"""
    service = get_gmail_service(credentials)
    results = service.users().labels().list(userId="me").execute()
    return results.get("labels", [])
