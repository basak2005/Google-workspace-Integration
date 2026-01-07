"""
Google Photos Service
Integrates with Google Photos Library API
"""
from googleapiclient.discovery import build
from typing import Any, Optional, List, Dict


def get_photos_service(credentials: Any):
    """Create Google Photos service instance"""
    return build("photoslibrary", "v1", credentials=credentials, static_discovery=False)


def list_albums(credentials: Any, page_size: int = 20, page_token: Optional[str] = None):
    """List user's albums"""
    service = get_photos_service(credentials)
    
    params: Dict[str, Any] = {"pageSize": page_size}
    if page_token:
        params["pageToken"] = page_token
    
    response = service.albums().list(**params).execute()
    
    albums = []
    for album in response.get("albums", []):
        albums.append({
            "id": album.get("id"),
            "title": album.get("title"),
            "product_url": album.get("productUrl"),
            "cover_photo_url": album.get("coverPhotoBaseUrl"),
            "media_items_count": album.get("mediaItemsCount", 0),
            "is_writeable": album.get("isWriteable", False)
        })
    
    return {
        "albums": albums,
        "next_page_token": response.get("nextPageToken")
    }


def get_album(credentials: Any, album_id: str):
    """Get album details"""
    service = get_photos_service(credentials)
    
    album = service.albums().get(albumId=album_id).execute()
    
    return {
        "id": album.get("id"),
        "title": album.get("title"),
        "product_url": album.get("productUrl"),
        "cover_photo_url": album.get("coverPhotoBaseUrl"),
        "media_items_count": album.get("mediaItemsCount", 0),
        "is_writeable": album.get("isWriteable", False)
    }


def create_album(credentials: Any, title: str):
    """Create a new album"""
    service = get_photos_service(credentials)
    
    body = {
        "album": {"title": title}
    }
    
    album = service.albums().create(body=body).execute()
    
    return {
        "id": album.get("id"),
        "title": album.get("title"),
        "product_url": album.get("productUrl"),
        "is_writeable": album.get("isWriteable", False)
    }


def list_media_items(credentials: Any, page_size: int = 25, page_token: Optional[str] = None):
    """List media items in the library"""
    service = get_photos_service(credentials)
    
    params: Dict[str, Any] = {"pageSize": page_size}
    if page_token:
        params["pageToken"] = page_token
    
    response = service.mediaItems().list(**params).execute()
    
    items = []
    for item in response.get("mediaItems", []):
        items.append({
            "id": item.get("id"),
            "filename": item.get("filename"),
            "description": item.get("description"),
            "mime_type": item.get("mimeType"),
            "base_url": item.get("baseUrl"),
            "product_url": item.get("productUrl"),
            "creation_time": item.get("mediaMetadata", {}).get("creationTime"),
            "width": item.get("mediaMetadata", {}).get("width"),
            "height": item.get("mediaMetadata", {}).get("height"),
            "is_video": "video" in item.get("mediaMetadata", {})
        })
    
    return {
        "media_items": items,
        "next_page_token": response.get("nextPageToken")
    }


def get_media_item(credentials: Any, media_item_id: str):
    """Get a specific media item"""
    service = get_photos_service(credentials)
    
    item = service.mediaItems().get(mediaItemId=media_item_id).execute()
    
    return {
        "id": item.get("id"),
        "filename": item.get("filename"),
        "description": item.get("description"),
        "mime_type": item.get("mimeType"),
        "base_url": item.get("baseUrl"),
        "product_url": item.get("productUrl"),
        "creation_time": item.get("mediaMetadata", {}).get("creationTime"),
        "width": item.get("mediaMetadata", {}).get("width"),
        "height": item.get("mediaMetadata", {}).get("height"),
        "is_video": "video" in item.get("mediaMetadata", {}),
        "camera_info": item.get("mediaMetadata", {}).get("photo", {})
    }


def search_media_items(credentials: Any, filters: Optional[Dict] = None, page_size: int = 25, page_token: Optional[str] = None):
    """
    Search media items with filters.
    filters can include:
    - dateFilter: {"dates": [{"year": 2024, "month": 1, "day": 15}]}
    - contentFilter: {"includedContentCategories": ["LANDSCAPES", "SELFIES", "PEOPLE"]}
    - mediaTypeFilter: {"mediaTypes": ["PHOTO" or "VIDEO"]}
    """
    service = get_photos_service(credentials)
    
    body: Dict[str, Any] = {"pageSize": page_size}
    if filters:
        body["filters"] = filters
    if page_token:
        body["pageToken"] = page_token
    
    response = service.mediaItems().search(body=body).execute()
    
    items = []
    for item in response.get("mediaItems", []):
        items.append({
            "id": item.get("id"),
            "filename": item.get("filename"),
            "mime_type": item.get("mimeType"),
            "base_url": item.get("baseUrl"),
            "product_url": item.get("productUrl"),
            "creation_time": item.get("mediaMetadata", {}).get("creationTime"),
            "width": item.get("mediaMetadata", {}).get("width"),
            "height": item.get("mediaMetadata", {}).get("height")
        })
    
    return {
        "media_items": items,
        "next_page_token": response.get("nextPageToken")
    }


def list_album_media_items(credentials: Any, album_id: str, page_size: int = 25, page_token: Optional[str] = None):
    """List media items in a specific album"""
    service = get_photos_service(credentials)
    
    body: Dict[str, Any] = {
        "albumId": album_id,
        "pageSize": page_size
    }
    if page_token:
        body["pageToken"] = page_token
    
    response = service.mediaItems().search(body=body).execute()
    
    items = []
    for item in response.get("mediaItems", []):
        items.append({
            "id": item.get("id"),
            "filename": item.get("filename"),
            "mime_type": item.get("mimeType"),
            "base_url": item.get("baseUrl"),
            "product_url": item.get("productUrl"),
            "creation_time": item.get("mediaMetadata", {}).get("creationTime"),
            "width": item.get("mediaMetadata", {}).get("width"),
            "height": item.get("mediaMetadata", {}).get("height")
        })
    
    return {
        "media_items": items,
        "next_page_token": response.get("nextPageToken")
    }


def list_shared_albums(credentials: Any, page_size: int = 20, page_token: Optional[str] = None):
    """List shared albums"""
    service = get_photos_service(credentials)
    
    params: Dict[str, Any] = {"pageSize": page_size}
    if page_token:
        params["pageToken"] = page_token
    
    response = service.sharedAlbums().list(**params).execute()
    
    albums = []
    for album in response.get("sharedAlbums", []):
        albums.append({
            "id": album.get("id"),
            "title": album.get("title"),
            "product_url": album.get("productUrl"),
            "cover_photo_url": album.get("coverPhotoBaseUrl"),
            "media_items_count": album.get("mediaItemsCount", 0),
            "share_info": album.get("shareInfo", {})
        })
    
    return {
        "shared_albums": albums,
        "next_page_token": response.get("nextPageToken")
    }
