import os
from dotenv import load_dotenv

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

GOOGLE_REDIRECT_URI = "http://localhost:8000/auth/callback"

# Google API Scopes - All products
SCOPES = [
    # Calendar & Meet
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    
    # Google Tasks
    "https://www.googleapis.com/auth/tasks",
    
    # Gmail
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    
    # Google Drive
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    
    # Google Contacts (People API)
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/contacts",
    
    # Google Sheets
    "https://www.googleapis.com/auth/spreadsheets",
    
    # YouTube
    "https://www.googleapis.com/auth/youtube.readonly",
    
    # Google Photos
    "https://www.googleapis.com/auth/photoslibrary.readonly",
    
    # Google Keep (Enterprise/Workspace only - not available for personal accounts)
    # "https://www.googleapis.com/auth/keep",
    
    # User Profile
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]
