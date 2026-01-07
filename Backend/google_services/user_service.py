"""
Google User Profile Service
Get user information from Google
"""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_user_service(credentials: Credentials):
    """Create Google OAuth2 service instance"""
    return build("oauth2", "v2", credentials=credentials)


def get_user_info(credentials: Credentials):
    """Get user profile information"""
    service = get_user_service(credentials)
    user_info = service.userinfo().get().execute()
    return {
        "id": user_info.get("id"),
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "locale": user_info.get("locale"),
    }
