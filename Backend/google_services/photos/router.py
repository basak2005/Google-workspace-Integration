"""
Google Photos API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from auth.router import get_credentials
from auth.dependencies import require_session
from google_services.photos_service import (
    list_albums,
    get_album,
    create_album,
    list_media_items,
    get_media_item,
    search_media_items,
    list_album_media_items,
    list_shared_albums,
)

router = APIRouter(prefix="/photos", tags=["Google Photos"])


class AlbumCreate(BaseModel):
    title: str


class MediaSearchFilters(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    media_type: Optional[str] = None  # "PHOTO" or "VIDEO"
    categories: Optional[List[str]] = None  # ["LANDSCAPES", "SELFIES", "PEOPLE", etc.]


@router.get("/albums")
def get_albums(page_size: int = 20, page_token: Optional[str] = None, session_id: str = Depends(require_session)):
    """List user's photo albums"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_albums(credentials, page_size, page_token)


@router.get("/albums/shared")
def get_shared_albums(page_size: int = 20, page_token: Optional[str] = None, session_id: str = Depends(require_session)):
    """List shared albums"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_shared_albums(credentials, page_size, page_token)


@router.get("/albums/{album_id}")
def get_album_details(album_id: str, session_id: str = Depends(require_session)):
    """Get details of a specific album"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_album(credentials, album_id)


@router.post("/albums")
def create_new_album(album: AlbumCreate, session_id: str = Depends(require_session)):
    """Create a new photo album"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return create_album(credentials, album.title)


@router.get("/albums/{album_id}/items")
def get_album_items(album_id: str, page_size: int = 25, page_token: Optional[str] = None, session_id: str = Depends(require_session)):
    """Get media items in an album"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_album_media_items(credentials, album_id, page_size, page_token)


@router.get("/media")
def get_media_items(page_size: int = 25, page_token: Optional[str] = None, session_id: str = Depends(require_session)):
    """List all media items in library"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_media_items(credentials, page_size, page_token)


@router.get("/media/{media_item_id}")
def get_media_item_details(media_item_id: str, session_id: str = Depends(require_session)):
    """Get details of a specific media item"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_media_item(credentials, media_item_id)


@router.post("/media/search")
def search_media(filters: MediaSearchFilters, session_id: str = Depends(require_session)):
    """
    Search media items with filters.
    Categories: LANDSCAPES, SELFIES, PEOPLE, PETS, WEDDINGS, BIRTHDAYS, DOCUMENTS, TRAVEL, ANIMALS, FOOD, etc.
    """
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    api_filters = {}
    
    if filters.year or filters.month or filters.day:
        date_filter = {}
        if filters.year:
            date_filter["year"] = filters.year
        if filters.month:
            date_filter["month"] = filters.month
        if filters.day:
            date_filter["day"] = filters.day
        api_filters["dateFilter"] = {"dates": [date_filter]}
    
    if filters.media_type:
        api_filters["mediaTypeFilter"] = {"mediaTypes": [filters.media_type]}
    
    if filters.categories:
        api_filters["contentFilter"] = {"includedContentCategories": filters.categories}
    
    return search_media_items(credentials, api_filters if api_filters else None)
