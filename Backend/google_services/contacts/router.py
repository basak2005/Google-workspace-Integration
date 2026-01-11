"""
Google Contacts API Routes (People API)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from auth.router import get_credentials
from auth.dependencies import require_session
from google_services.contacts_service import (
    list_contacts,
    get_contact,
    create_contact,
    delete_contact,
    search_contacts,
    get_other_contacts,
)

router = APIRouter(prefix="/contacts", tags=["Google Contacts"])


class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None


@router.get("/")
def get_contacts(max_results: int = 100, session_id: str = Depends(require_session)):
    """List all contacts"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_contacts(credentials, max_results)


@router.get("/search")
def search(query: str, max_results: int = 10, session_id: str = Depends(require_session)):
    """Search contacts by name or email"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return search_contacts(credentials, query, max_results)


@router.get("/other")
def other_contacts(max_results: int = 100, session_id: str = Depends(require_session)):
    """Get 'Other contacts' (auto-saved from emails)"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_other_contacts(credentials, max_results)


@router.get("/{resource_name:path}")
def get_contact_detail(resource_name: str, session_id: str = Depends(require_session)):
    """Get a specific contact by resource name (e.g., people/c123456)"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_contact(credentials, resource_name)


@router.post("/")
def add_contact(contact: ContactCreate, session_id: str = Depends(require_session)):
    """Create a new contact"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return create_contact(
        credentials,
        contact.name,
        contact.email,
        contact.phone,
        contact.organization
    )


@router.delete("/{resource_name:path}")
def remove_contact(resource_name: str, session_id: str = Depends(require_session)):
    """Delete a contact by resource name"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return delete_contact(credentials, resource_name)
