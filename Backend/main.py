from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from auth.router import router as auth_router, get_credentials
from google_services.calendar.router import router as calendar_router
from google_services.tasks.router import router as tasks_router
from google_services.gmail.router import router as gmail_router
from google_services.drive.router import router as drive_router
from google_services.contacts.router import router as contacts_router
from google_services.sheets.router import router as sheets_router
from google_services.youtube.router import router as youtube_router
from google_services.photos.router import router as photos_router
from google_services.maps import geocode_address
from google_services.user_service import get_user_info
from smart_assistant import get_smart_summary

app = FastAPI(
    title="Google Services API",
    description="""
    FastAPI backend integrating with Google APIs + Gemini AI.
    
    ## Products Integrated:
    - 📅 **Google Calendar** - Events & Meet links
    - ✅ **Google Tasks** - Task management
    - 📧 **Gmail** - Email management
    - 📁 **Google Drive** - File storage
    - 👥 **Google Contacts** - Contact management
    - 📊 **Google Sheets** - Spreadsheet operations
    - 🎬 **YouTube** - Video search & channel info
    - 📷 **Google Photos** - Photo albums & media
    - 🗺️ **Google Maps** - Geocoding
    - 👤 **User Profile** - Google account info
    - 🧠 **Smart Assistant** - AI-powered schedule analysis & task prioritization
    
    ## 🧠 NEW: Smart Assistant
    - `/smart-summary` - Get AI analysis of all your events & tasks with prioritized recommendations
    """,
    version="2.2.0"
)

# Get allowed origins from environment
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Parse multiple origins if needed
allowed_origins = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
]

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(calendar_router)
app.include_router(tasks_router)
app.include_router(gmail_router)
app.include_router(drive_router)
app.include_router(contacts_router)
app.include_router(sheets_router)
app.include_router(youtube_router)
app.include_router(photos_router)


@app.get("/", tags=["Info"])
def root():
    """API Information"""
    return {
        "message": "🧠 Google Services API with Smart Assistant",
        "docs": "/docs",
        "smart_assistant": "GET /smart-summary - AI-powered task analysis & prioritization",
        "environment": os.getenv("VERCEL_ENV", "development")
    }


# Vercel serverless handler
handler = app


@app.get("/smart-summary", tags=["🧠 Smart Assistant"])
def smart_summary(
    context: Optional[str] = Query(
        None, 
        description="Optional context like 'Focus on work tasks' or 'I have a deadline tomorrow'"
    )
):
    """
    🧠 **Get AI-Powered Smart Summary**
    
    Fetches all your Calendar events & Tasks, then uses Gemini AI to provide:
    - Summary of your schedule
    - Prioritized task order (what to do first and why)
    - Today's focus items
    - Smart recommendations
    - Warnings about conflicts
    
    **Optional**: Add `context` parameter to personalize.
    Example: `/smart-summary?context=I need to focus on the client project`
    """
    credentials = get_credentials()
    
    if not credentials:
        raise HTTPException(
            status_code=401, 
            detail={
                "error": "Not authenticated",
                "action": "Visit /auth/login to connect your Google account"
            }
        )
    
    try:
        return get_smart_summary(credentials, user_context=context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/me", tags=["User"])
def get_current_user():
    """Get current authenticated user's profile"""
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_user_info(credentials)


@app.get("/maps/geocode", tags=["Maps"])
def geocode(address: str):
    """Geocode an address using Google Maps API"""
    return geocode_address(address)
