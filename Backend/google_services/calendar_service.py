from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from typing import Optional, List
import uuid


def get_calendar_service(credentials: Credentials):
    """Create Google Calendar service instance"""
    return build("calendar", "v3", credentials=credentials)


def list_events(credentials: Credentials):
    """List upcoming calendar events"""
    service = get_calendar_service(credentials)
    
    # Get events starting from now
    now = datetime.utcnow().isoformat() + "Z"

    events = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events.get("items", [])


def create_event(
    credentials: Credentials,
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    timezone: str = "IST"
):
    """Create a calendar event
    
    Args:
        credentials: Google OAuth credentials
        summary: Event title
        start_datetime: Start time in ISO format (e.g., "2025-12-31T10:00:00")
        end_datetime: End time in ISO format (e.g., "2025-12-31T11:00:00")
        description: Optional event description
        location: Optional event location
        attendees: Optional list of attendee email addresses
        timezone: Timezone for the event (default: IST)
    
    Returns:
        Created event details
    """
    service = get_calendar_service(credentials)

    event = {
        "summary": summary,
        "start": {"dateTime": start_datetime, "timeZone": timezone},
        "end": {"dateTime": end_datetime, "timeZone": timezone},
    }

    if description:
        event["description"] = description
    
    if location:
        event["location"] = location
    
    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all" if attendees else "none",
    ).execute()

    return {
        "id": created_event.get("id"),
        "summary": created_event.get("summary"),
        "start": created_event.get("start"),
        "end": created_event.get("end"),
        "description": created_event.get("description"),
        "location": created_event.get("location"),
        "htmlLink": created_event.get("htmlLink"),
        "attendees": created_event.get("attendees", [])
    }


def create_meet_event(credentials: Credentials, summary: str = "FastAPI Google Meet", duration_minutes: int = 60):
    """Create a calendar event with Google Meet link"""
    service = get_calendar_service(credentials)

    # Create event starting 1 hour from now
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        "summary": summary,
        "start": {"dateTime": start_time.isoformat() + "Z", "timeZone": "UTC"},
        "end": {"dateTime": end_time.isoformat() + "Z", "timeZone": "UTC"},
        "conferenceData": {
            "createRequest": {"requestId": str(uuid.uuid4())}
        },
    }

    event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1,
    ).execute()

    return event.get("hangoutLink", "No Meet link generated")
