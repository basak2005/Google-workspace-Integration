"""
YouTube API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from auth.router import get_credentials
from auth.dependencies import require_session
from google_services.youtube_service import (
    search_videos,
    get_video_details,
    get_channel_info,
    list_playlists,
    get_playlist_items,
    list_subscriptions,
    get_liked_videos,
)

router = APIRouter(prefix="/youtube", tags=["YouTube"])


@router.get("/search")
def search(query: str, max_results: int = 10, order: str = "relevance", session_id: str = Depends(require_session)):
    """
    Search for YouTube videos.
    Order options: relevance, date, rating, viewCount, title
    """
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return search_videos(credentials, query, max_results, order)


@router.get("/videos/{video_id}")
def get_video(video_id: str, session_id: str = Depends(require_session)):
    """Get detailed information about a specific video"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    video = get_video_details(credentials, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.get("/channel")
def get_my_channel(session_id: str = Depends(require_session)):
    """Get the authenticated user's channel info"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    channel = get_channel_info(credentials)
    if not channel:
        raise HTTPException(status_code=404, detail="No channel found for this user")
    return channel


@router.get("/channel/{channel_id}")
def get_channel(channel_id: str, session_id: str = Depends(require_session)):
    """Get information about a specific channel"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    channel = get_channel_info(credentials, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


@router.get("/playlists")
def get_playlists(max_results: int = 25, session_id: str = Depends(require_session)):
    """List user's playlists"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_playlists(credentials, max_results)


@router.get("/playlists/{playlist_id}/items")
def get_playlist_videos(playlist_id: str, max_results: int = 50, session_id: str = Depends(require_session)):
    """Get videos in a playlist"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_playlist_items(credentials, playlist_id, max_results)


@router.get("/subscriptions")
def get_subscriptions(max_results: int = 25, session_id: str = Depends(require_session)):
    """List user's subscriptions"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_subscriptions(credentials, max_results)


@router.get("/liked")
def get_liked(session_id: str = Depends(require_session)):
    """Get user's liked videos"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_liked_videos(credentials)
