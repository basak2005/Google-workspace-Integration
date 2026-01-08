"""
Smart Assistant Service
Single endpoint that aggregates Google Calendar, Tasks & Gmail data 
and uses Gemini AI to provide intelligent task management advice
"""
from google import genai
from google.genai import types
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import GEMINI_API_KEY
import base64

# Configure Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def get_all_events(credentials: Credentials, days_ahead: int = 7) -> List[Dict[str, Any]]:
    """Fetch all calendar events for the next N days"""
    service = build("calendar", "v3", credentials=credentials)
    
    now = datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"
    
    events = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        timeMax=time_max,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    
    return events.get("items", [])


def get_all_tasks(credentials: Credentials) -> List[Dict[str, Any]]:
    """Fetch all pending tasks from all task lists"""
    service = build("tasks", "v1", credentials=credentials)
    
    all_tasks = []
    
    # Get all task lists
    task_lists = service.tasklists().list(maxResults=10).execute()
    
    for task_list in task_lists.get("items", []):
        list_id = task_list.get("id")
        list_name = task_list.get("title", "Unknown List")
        
        # Get tasks from this list
        tasks = service.tasks().list(
            tasklist=list_id,
            showCompleted=False,
            maxResults=100
        ).execute()
        
        for task in tasks.get("items", []):
            task["listName"] = list_name
            all_tasks.append(task)
    
    return all_tasks


def get_unread_emails(credentials: Credentials, max_results: int = 10) -> List[Dict[str, Any]]:
    """Fetch unread emails that contain tasks, action items, or pending work from clients"""
    service = build("gmail", "v1", credentials=credentials)
    
    # Query for unread emails with task-related keywords
    # Filters for emails likely containing pending tasks or client requests
    task_keywords = [
        "action required",
        "pending",
        "deadline",
        "urgent",
        "please review",
        "waiting for",
        "follow up",
        "task",
        "request",
        "asap",
        "due date",
        "by tomorrow",
        "needs your",
        "reminder",
        "priority",
        "important"
    ]
    
    # Build Gmail search query: is:unread AND (keyword1 OR keyword2 OR ...)
    keywords_query = " OR ".join([f'"{kw}"' for kw in task_keywords])
    search_query = f"is:unread ({keywords_query})"
    
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        q=search_query
    ).execute()
    
    messages = results.get("messages", [])
    
    detailed_emails = []
    for msg in messages:
        try:
            msg_detail = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="full"
            ).execute()
            
            headers = {h["name"]: h["value"] for h in msg_detail.get("payload", {}).get("headers", [])}
            
            # Extract body content
            body = ""
            payload = msg_detail.get("payload", {})
            
            if "parts" in payload:
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        data = part.get("body", {}).get("data", "")
                        if data:
                            body = base64.urlsafe_b64decode(data).decode("utf-8")
                        break
            elif "body" in payload and "data" in payload["body"]:
                body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
            
            # Truncate body to avoid token limits
            body = body[:500] if len(body) > 500 else body
            
            detailed_emails.append({
                "id": msg["id"],
                "from": headers.get("From", "Unknown"),
                "subject": headers.get("Subject", "No Subject"),
                "date": headers.get("Date", ""),
                "snippet": msg_detail.get("snippet", ""),
                "body": body
            })
        except Exception:
            continue
    
    return detailed_emails


def format_schedule_data(events: List[Dict], tasks: List[Dict], emails: List[Dict]) -> str:
    """Format events, tasks, and emails into a readable string for Gemini"""
    
    output = "📅 UPCOMING CALENDAR EVENTS:\n"
    output += "=" * 40 + "\n"
    
    if events:
        for event in events:
            summary = event.get('summary', 'Untitled Event')
            start = event.get('start', {})
            end = event.get('end', {})
            start_time = start.get('dateTime', start.get('date', 'TBD'))
            end_time = end.get('dateTime', end.get('date', ''))
            description = event.get('description', '')
            location = event.get('location', '')
            
            output += f"\n• {summary}\n"
            output += f"  📆 Start: {start_time}\n"
            if end_time:
                output += f"  ⏰ End: {end_time}\n"
            if location:
                output += f"  📍 Location: {location}\n"
            if description:
                output += f"  📝 Notes: {description[:100]}...\n" if len(description) > 100 else f"  📝 Notes: {description}\n"
    else:
        output += "No upcoming events scheduled.\n"
    
    output += "\n\n✅ PENDING TASKS:\n"
    output += "=" * 40 + "\n"
    
    if tasks:
        for task in tasks:
            title = task.get('title', 'Untitled Task')
            notes = task.get('notes', '')
            due = task.get('due', '')
            list_name = task.get('listName', 'Default')
            
            output += f"\n• {title}\n"
            output += f"  📋 List: {list_name}\n"
            if due:
                output += f"  📅 Due: {due}\n"
            if notes:
                output += f"  📝 Notes: {notes[:100]}...\n" if len(notes) > 100 else f"  📝 Notes: {notes}\n"
    else:
        output += "No pending tasks.\n"
    
    output += "\n\n📧 UNREAD EMAILS (Potential Tasks/Action Items):\n"
    output += "=" * 40 + "\n"
    
    if emails:
        for email in emails:
            sender = email.get('from', 'Unknown')
            subject = email.get('subject', 'No Subject')
            date = email.get('date', '')
            snippet = email.get('snippet', '')
            body = email.get('body', '')
            
            output += f"\n• From: {sender}\n"
            output += f"  📌 Subject: {subject}\n"
            output += f"  📆 Date: {date}\n"
            if snippet:
                output += f"  💬 Preview: {snippet[:150]}...\n" if len(snippet) > 150 else f"  💬 Preview: {snippet}\n"
            if body:
                output += f"  📄 Content: {body[:300]}...\n" if len(body) > 300 else f"  📄 Content: {body}\n"
    else:
        output += "No unread emails.\n"
    
    return output


def get_smart_summary(credentials: Credentials, user_context: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function: Fetches all events, tasks & unread emails, then uses Gemini to provide
    intelligent summary and task management recommendations.
    
    Returns a structured response with:
    - Raw data (events, tasks, emails)
    - AI-generated summary
    - Prioritized task order
    - Email-based action items
    - Productivity recommendations
    """
    
    # Fetch all data from Google services
    events = get_all_events(credentials)
    tasks = get_all_tasks(credentials)
    emails = get_unread_emails(credentials)
    
    # Format data for Gemini
    schedule_data = format_schedule_data(events, tasks, emails)
    
    # Gemini system instruction
    system_instruction = """You are an expert productivity coach and time management specialist.

Your job is to analyze the user's calendar events, tasks, AND unread emails, then provide:

1. **📊 SUMMARY** (2-3 sentences)
   - Brief overview of their schedule load
   - Key highlights and important deadlines
   - Note any urgent emails requiring action

2. **🎯 PRIORITIZED TASK ORDER** 
   - List tasks in the ORDER they should be completed
   - Include both explicit tasks AND action items from emails
   - Consider: urgency, importance, dependencies, and calendar conflicts
   - Use this format: 
     1. [TASK NAME] - Why this order (brief reason)
     2. [TASK NAME] - Why this order
     ...

3. **📧 EMAIL ACTION ITEMS**
   - Identify emails that contain tasks, requests, or pending work from clients
   - Extract specific action items from email content
   - Flag urgent client requests that need immediate attention
   - Format:
     • [SENDER]: [ACTION REQUIRED] - Priority level

4. **⚡ TODAY'S FOCUS** (if applicable)
   - Top 3 things to accomplish today
   - Include urgent email responses if needed
   - Realistic time estimates

5. **💡 SMART RECOMMENDATIONS**
   - Time blocking suggestions
   - Tasks that can be batched together
   - Emails that can be replied in batch
   - Potential scheduling conflicts to watch out for
   - Energy management tips (when to do deep work vs. light tasks)

6. **⚠️ WARNINGS** (if any)
   - Overcommitment alerts
   - Deadline risks
   - Urgent client emails awaiting response
   - Missing information (tasks without due dates, etc.)

Be concise, actionable, and encouraging. Use bullet points and emojis for easy scanning.
Focus on WHAT to do and WHEN to do it.
Pay special attention to client emails that may contain pending work or requests."""

    # Build the prompt
    prompt = f"""Please analyze my schedule and tasks, then give me a smart summary with prioritized recommendations.

Current Date/Time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}

{schedule_data}
"""
    
    if user_context:
        prompt += f"\n\nAdditional context from user: {user_context}"
    
    # Generate AI response
    config = types.GenerateContentConfig(system_instruction=system_instruction)
    
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )
    
    ai_summary = response.text or "Unable to generate summary."
    
    return {
        "success": True,
        "generated_at": datetime.now().isoformat(),
        "ai_analysis": ai_summary
    }
