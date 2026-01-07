"""
Google Drive API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth.router import get_credentials
from google_services.drive_service import (
    list_files,
    get_file,
    create_folder,
    delete_file,
    share_file,
    search_files,
    get_storage_quota,
)

router = APIRouter(prefix="/drive", tags=["Google Drive"])


class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None


class FileShare(BaseModel):
    email: str
    role: str = "reader"  # reader, writer, commenter


@router.get("/files")
def get_files(max_results: int = 10, query: str = "", folder_id: Optional[str] = None):
    """
    List files from Google Drive.
    Query examples: "mimeType='application/pdf'", "name contains 'report'"
    """
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_files(credentials, max_results, query, folder_id)


@router.get("/files/{file_id}")
def get_file_info(file_id: str):
    """Get file metadata by ID"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_file(credentials, file_id)


@router.post("/folders")
def create_new_folder(folder: FolderCreate):
    """Create a new folder"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return create_folder(credentials, folder.name, folder.parent_id)


@router.delete("/files/{file_id}")
def remove_file(file_id: str):
    """Delete a file or folder"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return delete_file(credentials, file_id)


@router.post("/files/{file_id}/share")
def share(file_id: str, share_info: FileShare):
    """Share a file with someone"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return share_file(credentials, file_id, share_info.email, share_info.role)


@router.get("/search")
def search(query: str, max_results: int = 10):
    """Search files by name or content"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return search_files(credentials, query, max_results)


@router.get("/quota")
def storage_quota():
    """Get storage usage information"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_storage_quota(credentials)
