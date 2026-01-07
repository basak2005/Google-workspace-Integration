"""
Google Keep API Routes
Official Google Keep API integration

API Reference: https://developers.google.com/keep/api/reference/rest
Available endpoints:
- Notes: list, get, create, delete
- Permissions: share/unshare notes
- Media: download attachments
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from auth.router import get_credentials
from google_services.keep_service import (
    list_notes,
    get_note,
    create_note,
    create_text_note,
    create_list_note,
    delete_note,
    add_permissions,
    remove_permissions,
    get_all_notes,
    format_note_for_display,
)

router = APIRouter(prefix="/keep", tags=["Keep"])


# ============== Pydantic Models ==============

class TextNoteCreate(BaseModel):
    title: str
    text: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Note",
                "text": "This is my note content"
            }
        }


class ListItem(BaseModel):
    text: str
    checked: bool = False


class ListNoteCreate(BaseModel):
    title: str
    items: List[ListItem]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Shopping List",
                "items": [
                    {"text": "Milk", "checked": False},
                    {"text": "Bread", "checked": False},
                    {"text": "Eggs", "checked": True}
                ]
            }
        }


class SharePermission(BaseModel):
    email: str
    role: str = "WRITER"  # OWNER or WRITER
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "role": "WRITER"
            }
        }


class ShareNoteRequest(BaseModel):
    members: List[SharePermission]


class RemovePermissionsRequest(BaseModel):
    permission_names: List[str]


# ============== Notes Endpoints ==============

@router.get("/notes")
def get_notes(
    page_size: int = 100,
    page_token: str = None,
    filter: str = None,
    credentials=Depends(get_credentials)
):
    """
    List notes from Google Keep
    
    - **page_size**: Maximum number of notes to return (default 100)
    - **page_token**: Token for pagination (from previous response)
    - **filter**: Filter string (e.g., "trashed=false")
    
    Returns notes with pagination token if more results exist.
    """
    try:
        result = list_notes(
            credentials,
            page_size=page_size,
            page_token=page_token,
            filter_str=filter
        )
        
        # Format notes for display
        formatted_notes = [format_note_for_display(note) for note in result.get("notes", [])]
        
        return {
            "notes": formatted_notes,
            "nextPageToken": result.get("nextPageToken"),
            "count": len(formatted_notes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes/all")
def get_all_notes_endpoint(
    include_trashed: bool = False,
    credentials=Depends(get_credentials)
):
    """
    Get all notes (handles pagination automatically)
    
    - **include_trashed**: Include trashed notes (default False)
    
    Warning: May take time for accounts with many notes.
    """
    try:
        notes = get_all_notes(credentials, include_trashed=include_trashed)
        formatted_notes = [format_note_for_display(note) for note in notes]
        
        return {
            "notes": formatted_notes,
            "total": len(formatted_notes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notes/{note_id}")
def get_single_note(
    note_id: str,
    credentials=Depends(get_credentials)
):
    """
    Get a specific note by ID
    
    - **note_id**: The note ID (with or without 'notes/' prefix)
    
    Returns full note details including content, permissions, and attachments.
    """
    try:
        note = get_note(credentials, note_id)
        return format_note_for_display(note)
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes/text")
def create_text_note_endpoint(
    note: TextNoteCreate,
    credentials=Depends(get_credentials)
):
    """
    Create a new text note
    
    - **title**: Note title
    - **text**: Note content
    
    Returns the created note.
    """
    try:
        created = create_text_note(credentials, title=note.title, text=note.text)
        return format_note_for_display(created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes/list")
def create_list_note_endpoint(
    note: ListNoteCreate,
    credentials=Depends(get_credentials)
):
    """
    Create a new checklist/list note
    
    - **title**: Note title
    - **items**: List of items with text and checked status
    
    Returns the created note.
    """
    try:
        items = [{"text": item.text, "checked": item.checked} for item in note.items]
        created = create_list_note(credentials, title=note.title, items=items)
        return format_note_for_display(created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes")
def create_note_endpoint(
    title: str,
    text: str = None,
    items: List[ListItem] = None,
    credentials=Depends(get_credentials)
):
    """
    Create a note (text or list)
    
    - **title**: Note title
    - **text**: Text content (for text notes)
    - **items**: List items (for list notes)
    
    Provide either text OR items, not both.
    """
    try:
        list_items = None
        if items:
            list_items = [{"text": item.text, "checked": item.checked} for item in items]
        
        created = create_note(
            credentials,
            title=title,
            text_content=text,
            list_items=list_items
        )
        return format_note_for_display(created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notes/{note_id}")
def delete_note_endpoint(
    note_id: str,
    credentials=Depends(get_credentials)
):
    """
    Delete a note (moves to trash)
    
    - **note_id**: The note ID to delete
    
    Returns confirmation of deletion.
    """
    try:
        result = delete_note(credentials, note_id)
        return result
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Permissions Endpoints ==============

@router.post("/notes/{note_id}/share")
def share_note(
    note_id: str,
    request: ShareNoteRequest,
    credentials=Depends(get_credentials)
):
    """
    Share a note with other users
    
    - **note_id**: The note ID to share
    - **members**: List of users with email and role (OWNER or WRITER)
    
    Returns created permissions.
    """
    try:
        members = [{"email": m.email, "role": m.role} for m in request.members]
        result = add_permissions(credentials, note_id, members)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notes/{note_id}/unshare")
def unshare_note(
    note_id: str,
    request: RemovePermissionsRequest,
    credentials=Depends(get_credentials)
):
    """
    Remove sharing permissions from a note
    
    - **note_id**: The note ID
    - **permission_names**: List of permission resource names to remove
    
    Returns confirmation.
    """
    try:
        result = remove_permissions(credentials, note_id, request.permission_names)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Info Endpoint ==============

@router.get("/info")
def keep_info():
    """
    Get Google Keep API information
    
    Returns available endpoints and usage information.
    """
    return {
        "service": "Google Keep API",
        "version": "v1",
        "documentation": "https://developers.google.com/keep/api/reference/rest",
        "note": "Google Keep API is primarily designed for enterprise (Google Workspace) use",
        "endpoints": {
            "GET /keep/notes": "List notes with pagination",
            "GET /keep/notes/all": "Get all notes (auto-pagination)",
            "GET /keep/notes/{note_id}": "Get specific note",
            "POST /keep/notes/text": "Create text note",
            "POST /keep/notes/list": "Create checklist note",
            "DELETE /keep/notes/{note_id}": "Delete note",
            "POST /keep/notes/{note_id}/share": "Share note with users",
            "POST /keep/notes/{note_id}/unshare": "Remove sharing permissions"
        },
        "note_types": {
            "TEXT": "Simple text notes with title and content",
            "LIST": "Checklist notes with items that can be checked/unchecked"
        }
    }
