"""
YouTube Service
Integrates with YouTube Data API v3
"""
from googleapiclient.discovery import build
from typing import Any, Optional


def get_youtube_service(credentials: Any):
    """Create YouTube service instance"""
    return build("youtube", "v3", credentials=credentials)


def search_videos(credentials: Any, query: str, max_results: int = 10, order: str = "relevance"):
    """
    Search for YouTube videos
    order options: relevance, date, rating, viewCount, title
    """
    service = get_youtube_service(credentials)
    
    response = service.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results,
        order=order
    ).execute()
    
    videos = []
    for item in response.get("items", []):
        videos.append({
            "id": item.get("id", {}).get("videoId"),
            "title": item.get("snippet", {}).get("title"),
            "description": item.get("snippet", {}).get("description"),
            "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url"),
            "channel_title": item.get("snippet", {}).get("channelTitle"),
            "published_at": item.get("snippet", {}).get("publishedAt"),
            "url": f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId')}"
        })
    
    return {
        "total_results": response.get("pageInfo", {}).get("totalResults"),
        "videos": videos,
        "next_page_token": response.get("nextPageToken")
    }


def get_video_details(credentials: Any, video_id: str):
    """Get detailed information about a video"""
    service = get_youtube_service(credentials)
    
    response = service.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    ).execute()
    
    if not response.get("items"):
        return None
    
    item = response["items"][0]
    
    return {
        "id": item.get("id"),
        "title": item.get("snippet", {}).get("title"),
        "description": item.get("snippet", {}).get("description"),
        "channel_id": item.get("snippet", {}).get("channelId"),
        "channel_title": item.get("snippet", {}).get("channelTitle"),
        "published_at": item.get("snippet", {}).get("publishedAt"),
        "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("high", {}).get("url"),
        "duration": item.get("contentDetails", {}).get("duration"),
        "view_count": item.get("statistics", {}).get("viewCount"),
        "like_count": item.get("statistics", {}).get("likeCount"),
        "comment_count": item.get("statistics", {}).get("commentCount"),
        "tags": item.get("snippet", {}).get("tags", []),
        "url": f"https://www.youtube.com/watch?v={item.get('id')}"
    }


def get_channel_info(credentials: Any, channel_id: Optional[str] = None):
    """Get channel information (defaults to authenticated user's channel if no ID)"""
    service = get_youtube_service(credentials)
    
    if channel_id:
        response = service.channels().list(
            part="snippet,contentDetails,statistics",
            id=channel_id
        ).execute()
    else:
        response = service.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        ).execute()
    
    if not response.get("items"):
        return None
    
    item = response["items"][0]
    
    return {
        "id": item.get("id"),
        "title": item.get("snippet", {}).get("title"),
        "description": item.get("snippet", {}).get("description"),
        "custom_url": item.get("snippet", {}).get("customUrl"),
        "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url"),
        "subscriber_count": item.get("statistics", {}).get("subscriberCount"),
        "video_count": item.get("statistics", {}).get("videoCount"),
        "view_count": item.get("statistics", {}).get("viewCount"),
        "uploads_playlist": item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    }


def list_playlists(credentials: Any, max_results: int = 25):
    """List user's playlists"""
    service = get_youtube_service(credentials)
    
    response = service.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=max_results
    ).execute()
    
    playlists = []
    for item in response.get("items", []):
        playlists.append({
            "id": item.get("id"),
            "title": item.get("snippet", {}).get("title"),
            "description": item.get("snippet", {}).get("description"),
            "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url"),
            "video_count": item.get("contentDetails", {}).get("itemCount"),
            "published_at": item.get("snippet", {}).get("publishedAt")
        })
    
    return {"playlists": playlists, "total": len(playlists)}


def get_playlist_items(credentials: Any, playlist_id: str, max_results: int = 50):
    """Get videos in a playlist"""
    service = get_youtube_service(credentials)
    
    response = service.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=max_results
    ).execute()
    
    items = []
    for item in response.get("items", []):
        items.append({
            "video_id": item.get("contentDetails", {}).get("videoId"),
            "title": item.get("snippet", {}).get("title"),
            "description": item.get("snippet", {}).get("description"),
            "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url"),
            "position": item.get("snippet", {}).get("position"),
            "added_at": item.get("contentDetails", {}).get("videoPublishedAt"),
            "url": f"https://www.youtube.com/watch?v={item.get('contentDetails', {}).get('videoId')}"
        })
    
    return {
        "items": items,
        "total": response.get("pageInfo", {}).get("totalResults"),
        "next_page_token": response.get("nextPageToken")
    }


def list_subscriptions(credentials: Any, max_results: int = 25):
    """List user's subscriptions"""
    service = get_youtube_service(credentials)
    
    response = service.subscriptions().list(
        part="snippet",
        mine=True,
        maxResults=max_results
    ).execute()
    
    subscriptions = []
    for item in response.get("items", []):
        subscriptions.append({
            "channel_id": item.get("snippet", {}).get("resourceId", {}).get("channelId"),
            "title": item.get("snippet", {}).get("title"),
            "description": item.get("snippet", {}).get("description"),
            "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url")
        })
    
    return {"subscriptions": subscriptions, "total": len(subscriptions)}


def get_liked_videos(credentials: Any, max_results: int = 25):
    """Get user's liked videos"""
    service = get_youtube_service(credentials)
    
    response = service.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like",
        maxResults=max_results
    ).execute()
    
    videos = []
    for item in response.get("items", []):
        videos.append({
            "id": item.get("id"),
            "title": item.get("snippet", {}).get("title"),
            "channel_title": item.get("snippet", {}).get("channelTitle"),
            "thumbnail": item.get("snippet", {}).get("thumbnails", {}).get("default", {}).get("url"),
            "view_count": item.get("statistics", {}).get("viewCount"),
            "url": f"https://www.youtube.com/watch?v={item.get('id')}"
        })
    
    return {"videos": videos, "total": len(videos)}
