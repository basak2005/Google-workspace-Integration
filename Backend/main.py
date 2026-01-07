from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router, get_credentials
from google_services.calendar.router import router as calendar_router
from google_services.tasks.router import router as tasks_router
from google_services.gmail.router import router as gmail_router
from google_services.drive.router import router as drive_router
from google_services.contacts.router import router as contacts_router
from google_services.sheets.router import router as sheets_router
from google_services.youtube.router import router as youtube_router
from google_services.photos.router import router as photos_router
# Google Keep API is restricted to Google Workspace accounts only
# from google_services.keep.router import router as keep_router
from google_services.maps import geocode_address
from google_services.user_service import get_user_info

app = FastAPI(
    title="Google Services API",
    description="""
    FastAPI backend integrating with Google APIs.
    
    ## Products Integrated:
    - 📅 **Google Calendar** - Events & Meet links
    - ✅ **Google Tasks** - Task management
    - 📧 **Gmail** - Email management
    - 📁 **Google Drive** - File storage
    - 👥 **Google Contacts** - Contact management
    - 📊 **Google Sheets** - Spreadsheet operations
    - 🎬 **YouTube** - Video search & channel info
    - 📷 **Google Photos** - Photo albums & media
    - 📝 **Google Keep** - ⚠️ Workspace only (not available for personal accounts)
    - 🗺️ **Google Maps** - Geocoding
    - 👤 **User Profile** - Google account info
    
    ## Authentication Flow:
    1. Call `/auth/login` to start OAuth (auto-redirects)
    2. User authorizes in browser
    3. Google redirects to `/auth/callback`
    4. Use other endpoints with stored credentials
    
    ## Session Persistence:
    - Credentials are stored in SQLite database
    - Sessions persist across server restarts
    - Tokens auto-refresh when expired
    """,
    version="2.0.0"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Configure for your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(calendar_router)
app.include_router(tasks_router)
app.include_router(gmail_router)
app.include_router(drive_router)
app.include_router(contacts_router)
app.include_router(sheets_router)
app.include_router(youtube_router)
app.include_router(photos_router)
# Google Keep API is restricted to Google Workspace accounts only
# app.include_router(keep_router)


@app.get("/", tags=["Health"])
def root():
    """Health check and API documentation endpoint"""
    return {
        "docs": "Visit /docs for interactive Swagger UI",
        "authentication": {
            "description": "Start here! Authenticate with Google OAuth",
            "endpoints": {
                "GET /auth/login": "Start OAuth flow (auto-redirects to Google)",
                "GET /auth/login?force=true": "Force re-authentication (use after adding new scopes)",
                "GET /auth/callback": "OAuth callback handler (automatic)",
                "GET /auth/status": "Check if user is authenticated",
                "POST /auth/logout": "Clear stored credentials"
            }
        },
        "calendar": {
            "description": "📅 Google Calendar - Manage events & meetings",
            "endpoints": {
                "GET /calendar/events": "List upcoming events (?max_results=10)",
                "POST /calendar/events": "Create event (body: {summary, start, end, description?, with_meet?})",
                "DELETE /calendar/events/{event_id}": "Delete an event"
            }
        },
        "tasks": {
            "description": "✅ Google Tasks - Task management",
            "endpoints": {
                "GET /tasks/lists": "Get all task lists",
                "GET /tasks/lists/{tasklist_id}/tasks": "Get tasks in a list",
                "POST /tasks/lists/{tasklist_id}/tasks": "Create task (body: {title, notes?, due?})",
                "PUT /tasks/lists/{tasklist_id}/tasks/{task_id}": "Update task",
                "DELETE /tasks/lists/{tasklist_id}/tasks/{task_id}": "Delete task"
            }
        },
        "gmail": {
            "description": "📧 Gmail - Email management",
            "endpoints": {
                "GET /gmail/messages": "List messages (?max_results=10&query=is:unread)",
                "GET /gmail/messages/{message_id}": "Get full message content",
                "POST /gmail/send": "Send email (body: {to, subject, body})",
                "GET /gmail/labels": "Get all labels/folders"
            }
        },
        "drive": {
            "description": "📁 Google Drive - File storage",
            "endpoints": {
                "GET /drive/files": "List files (?max_results=10&query=name contains 'doc')",
                "GET /drive/files/{file_id}": "Get file metadata",
                "DELETE /drive/files/{file_id}": "Delete file/folder",
                "POST /drive/folders": "Create folder (body: {name, parent_id?})",
                "POST /drive/files/{file_id}/share": "Share file (body: {email, role})",
                "GET /drive/search": "Search files (?query=mimeType='application/pdf')",
                "GET /drive/quota": "Get storage quota info"
            }
        },
        "contacts": {
            "description": "👥 Google Contacts - Contact management",
            "endpoints": {
                "GET /contacts/": "List contacts (?max_results=100)",
                "GET /contacts/search": "Search contacts (?query=John)",
                "GET /contacts/other": "List 'Other contacts'",
                "GET /contacts/{resource_name}": "Get contact details",
                "POST /contacts/": "Create contact (body: {name, email?, phone?, organization?})",
                "DELETE /contacts/{resource_name}": "Delete contact"
            }
        },
        "sheets": {
            "description": "📊 Google Sheets - Spreadsheet operations",
            "endpoints": {
                "POST /sheets/": "Create spreadsheet (body: {title, sheets?})",
                "GET /sheets/{spreadsheet_id}": "Get spreadsheet metadata",
                "GET /sheets/{spreadsheet_id}/read": "Read data (?range=Sheet1!A1:D10)",
                "POST /sheets/{spreadsheet_id}/write": "Write data (body: {range, values: [[...]]})",
                "POST /sheets/{spreadsheet_id}/append": "Append rows (body: {range, values})",
                "DELETE /sheets/{spreadsheet_id}/clear": "Clear range (?range=Sheet1!A1:D10)",
                "POST /sheets/{spreadsheet_id}/sheets": "Add new sheet tab (body: {title})"
            }
        },
        "youtube": {
            "description": "🎬 YouTube - Video search & channel info",
            "endpoints": {
                "GET /youtube/search": "Search videos (?query=python&max_results=10&order=relevance)",
                "GET /youtube/videos/{video_id}": "Get video details",
                "GET /youtube/channel": "Get your channel info",
                "GET /youtube/channel/{channel_id}": "Get any channel info",
                "GET /youtube/playlists": "List your playlists",
                "GET /youtube/playlists/{playlist_id}/items": "Get videos in playlist",
                "GET /youtube/subscriptions": "List your subscriptions",
                "GET /youtube/liked": "Get your liked videos"
            }
        },
        "photos": {
            "description": "📷 Google Photos - Photo albums & media",
            "endpoints": {
                "GET /photos/albums": "List albums (?page_size=20)",
                "POST /photos/albums": "Create album (body: {title})",
                "GET /photos/albums/shared": "List shared albums",
                "GET /photos/albums/{album_id}": "Get album details",
                "GET /photos/albums/{album_id}/items": "Get photos in album",
                "GET /photos/media": "List all media items",
                "GET /photos/media/{media_item_id}": "Get media details",
                "POST /photos/media/search": "Search (body: {year?, month?, media_type?, categories?})"
            }
        },
        "keep": {
            "description": "📝 Google Keep - Notes & checklists",
            "status": "⚠️ NOT AVAILABLE - Google Keep API is restricted to Google Workspace (enterprise) accounts only",
            "note": "Personal Gmail accounts cannot use the official Keep API. Google has not released a public API for personal Keep users.",
            "alternatives": [
                "Use Google Tasks API instead for task/checklist management",
                "Use unofficial 'gkeepapi' library (requires app password, less reliable)"
            ]
        },
        "maps_and_user": {
            "description": "🗺️ Maps & User Profile",
            "endpoints": {
                "GET /maps/geocode": "Geocode address (?address=1600 Amphitheatre Parkway)",
                "GET /user/me": "Get authenticated user's Google profile"
            }
        }
    }


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
