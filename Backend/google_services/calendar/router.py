from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from auth.router import get_credentials
from google_services.calendar_service import list_events, create_meet_event, create_event

router = APIRouter(prefix="/calendar", tags=["Calendar"])


class CreateEventRequest(BaseModel):
    summary: str
    start_datetime: str  # ISO format: "2025-12-31T10:00:00"
    end_datetime: str    # ISO format: "2025-12-31T11:00:00"
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None  # List of email addresses
    timezone: Optional[str] = "IST"


@router.get("/events")
def get_events():
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return list_events(credentials)


@router.post("/events")
def create_calendar_event(request: CreateEventRequest):
    """Create a new calendar event"""
    credentials = get_credentials()
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
def create_meet():
    credentials = get_credentials()
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return {"meet_link": create_meet_event(credentials)}
