"""
Google Keep Service
Integrates with the official Google Keep API

Official API Reference: https://developers.google.com/keep/api/reference/rest
API Endpoints:
- v1.notes: create, delete, get, list
- v1.notes.permissions: batchCreate, batchDelete
- v1.media: download attachments

Note: Google Keep API is primarily for enterprise use (Google Workspace)
"""
from googleapiclient.discovery import build
from typing import Any, Optional, List


def get_keep_service(credentials: Any):
    """Create Google Keep service instance"""
    return build("keep", "v1", credentials=credentials)


# ============== NOTES ==============

def list_notes(credentials: Any, page_size: int = 100, page_token: str = None, filter_str: str = None) -> dict:
    """
    List all notes from Google Keep
    
    Args:
        credentials: Google OAuth credentials
        page_size: Maximum number of notes to return (default 100)
        page_token: Token for pagination
        filter_str: Filter string (e.g., "trashed=false" or "create_time > 2024-01-01")
    
    Returns:
        dict with notes list and nextPageToken
    """
    service = get_keep_service(credentials)
    
    params = {"pageSize": page_size}
    if page_token:
        params["pageToken"] = page_token
    if filter_str:
        params["filter"] = filter_str
    
    result = service.notes().list(**params).execute()
    
    return {
        "notes": result.get("notes", []),
        "nextPageToken": result.get("nextPageToken")
    }


def get_note(credentials: Any, note_id: str) -> dict:
    """
    Get a specific note by ID
    
    Args:
        credentials: Google OAuth credentials
        note_id: The note ID (format: notes/{note_id})
    
    Returns:
        Note object with all details
    """
    service = get_keep_service(credentials)
    
    # Ensure proper name format
    name = note_id if note_id.startswith("notes/") else f"notes/{note_id}"
    
    return service.notes().get(name=name).execute()


def create_note(
    credentials: Any,
    title: str = "",
    text_content: str = None,
    list_items: List[dict] = None
) -> dict:
    """
    Create a new note in Google Keep
    
    Args:
        credentials: Google OAuth credentials
        title: Note title
        text_content: Text content for a text note
        list_items: List of items for a list note
                   Each item: {"text": "item text", "checked": False}
    
    Returns:
        Created note object
    
    Note Structure:
    - TextNote: {"title": "...", "body": {"text": {"text": "content"}}}
    - ListNote: {"title": "...", "body": {"list": {"listItems": [...]}}}
    """
    service = get_keep_service(credentials)
    
    note_body = {"title": title}
    
    if list_items:
        # Create a list note
        formatted_items = []
        for item in list_items:
            formatted_items.append({
                "text": {"text": item.get("text", "")},
                "checked": item.get("checked", False)
            })
        note_body["body"] = {
            "list": {
                "listItems": formatted_items
            }
        }
    elif text_content:
        # Create a text note
        note_body["body"] = {
            "text": {
                "text": text_content
            }
        }
    
    return service.notes().create(body=note_body).execute()


def create_text_note(credentials: Any, title: str, text: str) -> dict:
    """
    Create a simple text note
    
    Args:
        credentials: Google OAuth credentials
        title: Note title
        text: Note text content
    
    Returns:
        Created note object
    """
    return create_note(credentials, title=title, text_content=text)


def create_list_note(credentials: Any, title: str, items: List[dict]) -> dict:
    """
    Create a checklist/list note
    
    Args:
        credentials: Google OAuth credentials
        title: Note title
        items: List of items [{"text": "item", "checked": False}, ...]
    
    Returns:
        Created note object
    """
    return create_note(credentials, title=title, list_items=items)


def delete_note(credentials: Any, note_id: str) -> dict:
    """
    Delete a note (moves to trash)
    
    Args:
        credentials: Google OAuth credentials
        note_id: The note ID
    
    Returns:
        Empty dict on success
    """
    service = get_keep_service(credentials)
    
    name = note_id if note_id.startswith("notes/") else f"notes/{note_id}"
    
    service.notes().delete(name=name).execute()
    return {"status": "deleted", "note_id": note_id}


# ============== PERMISSIONS ==============

def add_permissions(
    credentials: Any,
    note_id: str,
    members: List[dict]
) -> dict:
    """
    Share a note with other users
    
    Args:
        credentials: Google OAuth credentials
        note_id: The note ID
        members: List of members to add
                Each: {"email": "user@example.com", "role": "WRITER"}
                Roles: OWNER, WRITER
    
    Returns:
        Created permissions
    """
    service = get_keep_service(credentials)
    
    name = note_id if note_id.startswith("notes/") else f"notes/{note_id}"
    
    requests = []
    for member in members:
        requests.append({
            "permission": {
                "email": member.get("email"),
                "role": member.get("role", "WRITER")
            }
        })
    
    result = service.notes().permissions().batchCreate(
        parent=name,
        body={"requests": requests}
    ).execute()
    
    return result


def remove_permissions(
    credentials: Any,
    note_id: str,
    permission_names: List[str]
) -> dict:
    """
    Remove sharing permissions from a note
    
    Args:
        credentials: Google OAuth credentials
        note_id: The note ID
        permission_names: List of permission resource names to remove
    
    Returns:
        Empty dict on success
    """
    service = get_keep_service(credentials)
    
    name = note_id if note_id.startswith("notes/") else f"notes/{note_id}"
    
    service.notes().permissions().batchDelete(
        parent=name,
        body={"names": permission_names}
    ).execute()
    
    return {"status": "permissions_removed"}


# ============== ATTACHMENTS ==============

def download_attachment(credentials: Any, attachment_name: str) -> bytes:
    """
    Download an attachment from a note
    
    Args:
        credentials: Google OAuth credentials
        attachment_name: Full resource name (notes/{note_id}/attachments/{attachment_id})
    
    Returns:
        Attachment content as bytes
    """
    service = get_keep_service(credentials)
    
    response = service.media().download(name=attachment_name).execute()
    return response


# ============== HELPER FUNCTIONS ==============

def get_all_notes(credentials: Any, include_trashed: bool = False) -> List[dict]:
    """
    Get all notes (handles pagination automatically)
    
    Args:
        credentials: Google OAuth credentials
        include_trashed: Whether to include trashed notes
    
    Returns:
        List of all notes
    """
    all_notes = []
    page_token = None
    
    filter_str = None if include_trashed else "trashed=false"
    
    while True:
        result = list_notes(
            credentials, 
            page_size=100, 
            page_token=page_token,
            filter_str=filter_str
        )
        all_notes.extend(result.get("notes", []))
        
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    
    return all_notes


def format_note_for_display(note: dict) -> dict:
    """
    Format a note for easier display
    
    Args:
        note: Raw note object from API
    
    Returns:
        Simplified note dict
    """
    formatted = {
        "id": note.get("name", "").replace("notes/", ""),
        "name": note.get("name"),
        "title": note.get("title", ""),
        "createTime": note.get("createTime"),
        "updateTime": note.get("updateTime"),
        "trashed": note.get("trashed", False),
    }
    
    body = note.get("body", {})
    
    # Check if it's a text note or list note
    if "text" in body:
        formatted["type"] = "TEXT"
        formatted["content"] = body["text"].get("text", "")
    elif "list" in body:
        formatted["type"] = "LIST"
        items = []
        for item in body["list"].get("listItems", []):
            items.append({
                "text": item.get("text", {}).get("text", ""),
                "checked": item.get("checked", False)
            })
        formatted["items"] = items
    
    # Include permissions if present
    if "permissions" in note:
        formatted["permissions"] = note["permissions"]
    
    # Include attachments info if present
    if "attachments" in note:
        formatted["attachments"] = [
            {
                "name": att.get("name"),
                "mimeType": att.get("mimeType", [])
            }
            for att in note["attachments"]
        ]
    
    return formatted
