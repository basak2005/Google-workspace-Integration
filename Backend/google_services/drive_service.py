"""
Google Drive Service
Integrates with Drive API for file management
"""
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from typing import Any, Optional, Dict, List
import io


def get_drive_service(credentials: Any):
    """Create Google Drive service instance"""
    return build("drive", "v3", credentials=credentials)


def list_files(credentials: Any, max_results: int = 10, query: str = "", folder_id: Optional[str] = None):
    """
    List files from Google Drive
    query examples: "mimeType='application/pdf'", "name contains 'report'"
    """
    service = get_drive_service(credentials)
    
    q = query
    if folder_id:
        q = f"'{folder_id}' in parents" + (f" and {query}" if query else "")
    
    results = service.files().list(
        pageSize=max_results,
        q=q if q else None,
        fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents)"
    ).execute()
    
    return results.get("files", [])


def get_file(credentials: Any, file_id: str):
    """Get file metadata by ID"""
    service = get_drive_service(credentials)
    
    file = service.files().get(
        fileId=file_id,
        fields="id, name, mimeType, size, createdTime, modifiedTime, webViewLink, webContentLink, parents, description"
    ).execute()
    
    return file


def create_folder(credentials: Any, name: str, parent_id: Optional[str] = None):
    """Create a new folder"""
    service = get_drive_service(credentials)
    
    file_metadata: Dict[str, Any] = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    
    if parent_id:
        file_metadata["parents"] = [parent_id]
    
    folder = service.files().create(
        body=file_metadata,
        fields="id, name, webViewLink"
    ).execute()
    
    return folder


def upload_file(credentials: Any, file_path: str, name: Optional[str] = None, folder_id: Optional[str] = None, mime_type: Optional[str] = None):
    """Upload a file to Google Drive"""
    service = get_drive_service(credentials)
    
    file_metadata: Dict[str, Any] = {"name": name or file_path.split("/")[-1]}
    
    if folder_id:
        file_metadata["parents"] = [folder_id]
    
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink"
    ).execute()
    
    return file


def delete_file(credentials: Any, file_id: str):
    """Delete a file or folder"""
    service = get_drive_service(credentials)
    service.files().delete(fileId=file_id).execute()
    return {"message": "File deleted successfully"}


def share_file(credentials: Any, file_id: str, email: str, role: str = "reader"):
    """
    Share a file with someone
    role: "reader", "writer", "commenter"
    """
    service = get_drive_service(credentials)
    
    permission = {
        "type": "user",
        "role": role,
        "emailAddress": email
    }
    
    result = service.permissions().create(
        fileId=file_id,
        body=permission,
        sendNotificationEmail=True
    ).execute()
    
    return {"permission_id": result["id"], "status": "shared"}


def search_files(credentials: Any, query: str, max_results: int = 10):
    """Search files by name or content"""
    service = get_drive_service(credentials)
    
    results = service.files().list(
        pageSize=max_results,
        q=f"name contains '{query}' or fullText contains '{query}'",
        fields="files(id, name, mimeType, webViewLink)"
    ).execute()
    
    return results.get("files", [])


def get_storage_quota(credentials: Any):
    """Get storage usage information"""
    service = get_drive_service(credentials)
    
    about = service.about().get(fields="storageQuota, user").execute()
    
    quota = about.get("storageQuota", {})
    return {
        "limit": quota.get("limit"),
        "usage": quota.get("usage"),
        "usage_in_drive": quota.get("usageInDrive"),
        "usage_in_trash": quota.get("usageInDriveTrash"),
        "user": about.get("user", {}).get("emailAddress")
    }
