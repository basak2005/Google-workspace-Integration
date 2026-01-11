"""
Google Tasks API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from googleapiclient.errors import HttpError
from auth.router import get_credentials
from auth.dependencies import require_session
from google_services.tasks_service import (
    list_task_lists,
    list_tasks,
    create_task,
    complete_task,
    delete_task,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskCreate(BaseModel):
    title: str
    notes: str = ""
    task_list_id: str = "@default"


@router.get("/lists")
def get_task_lists(session_id: str = Depends(require_session)):
    """Get all task lists"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated. Visit /auth/login first.")
    try:
        return list_task_lists(credentials)
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))


@router.get("/")
def get_tasks(task_list_id: str = "@default", session_id: str = Depends(require_session)):
    """Get all tasks in a task list"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated. Visit /auth/login first.")
    try:
        return list_tasks(credentials, task_list_id)
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))


@router.post("/")
def add_task(task: TaskCreate, session_id: str = Depends(require_session)):
    """Create a new task"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated. Visit /auth/login first.")
    try:
        return create_task(
            credentials,
            title=task.title,
            notes=task.notes,
            task_list_id=task.task_list_id
        )
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))


@router.put("/{task_id}/complete")
def mark_complete(task_id: str, task_list_id: str = "@default", session_id: str = Depends(require_session)):
    """Mark a task as completed"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated. Visit /auth/login first.")
    try:
        return complete_task(credentials, task_id, task_list_id)
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))


@router.delete("/{task_id}")
def remove_task(task_id: str, task_list_id: str = "@default", session_id: str = Depends(require_session)):
    """Delete a task"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated. Visit /auth/login first.")
    try:
        return delete_task(credentials, task_id, task_list_id)
    except HttpError as e:
        raise HTTPException(status_code=e.resp.status, detail=str(e))
