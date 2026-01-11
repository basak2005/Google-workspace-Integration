from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from auth.router import get_credentials
from auth.dependencies import require_session
from google_services.calendar_service import list_events, create_meet_event, create_event, delete_event

router = APIRouter(prefix="/calendar", tags=["Calendar"])


class CreateEventRequest(BaseModel):
    summary: str
    start_datetime: str  # ISO format: "2025-12-31T10:00:00"
    end_datetime: str    # ISO format: "2025-12-31T11:00:00"
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None  # List of email addresses
    timezone: Optional[str] = "IST"


class CreateMeetRequest(BaseModel):
    summary: str  # Name of the Google Meet meeting
    duration_minutes: Optional[int] = 60  # Duration in minutes (default: 60)


@router.get("/events")
def get_events(session_id: str = Depends(require_session)):
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_events(credentials)


@router.post("/events")
def create_calendar_event(request: CreateEventRequest, session_id: str = Depends(require_session)):
    """Create a new calendar event"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    return create_event(
        credentials=credentials,
        summary=request.summary,
        start_datetime=request.start_datetime,
        end_datetime=request.end_datetime,
        description=request.description,
        location=request.location,
        attendees=request.attendees,
        timezone=request.timezone or "IST"
    )


@router.post("/meet")
def create_meet(request: CreateMeetRequest, session_id: str = Depends(require_session)):
    """Create a Google Meet event with a custom name"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return {"meet_link": create_meet_event(credentials, summary=request.summary, duration_minutes=request.duration_minutes or 60)}


@router.delete("/events/{event_id}")
def delete_calendar_event(event_id: str, session_id: str = Depends(require_session)):
    """Delete a calendar event by ID"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    try:
        return delete_event(credentials, event_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Event not found or could not be deleted: {str(e)}")
