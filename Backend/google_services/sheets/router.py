"""
Google Sheets API Routes
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from auth.router import get_credentials
from auth.dependencies import require_session
from google_services.sheets_service import (
    get_spreadsheet,
    read_range,
    write_range,
    append_rows,
    clear_range,
    create_spreadsheet,
    add_sheet,
)

router = APIRouter(prefix="/sheets", tags=["Google Sheets"])


class WriteData(BaseModel):
    range: str
    values: List[List]


class AppendData(BaseModel):
    range: str
    values: List[List]


class SpreadsheetCreate(BaseModel):
    title: str
    sheets: Optional[List[str]] = None


class SheetAdd(BaseModel):
    title: str


@router.get("/{spreadsheet_id}")
def get_sheet_info(spreadsheet_id: str, session_id: str = Depends(require_session)):
    """Get spreadsheet metadata"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return get_spreadsheet(credentials, spreadsheet_id)


@router.get("/{spreadsheet_id}/read")
def read_data(spreadsheet_id: str, range: str = "Sheet1", session_id: str = Depends(require_session)):
    """
    Read data from a spreadsheet range.
    Range examples: "Sheet1!A1:D10", "Sheet1", "A1:B5"
    """
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return read_range(credentials, spreadsheet_id, range)


@router.post("/{spreadsheet_id}/write")
def write_data(spreadsheet_id: str, data: WriteData, session_id: str = Depends(require_session)):
    """Write data to a spreadsheet range"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return write_range(credentials, spreadsheet_id, data.range, data.values)


@router.post("/{spreadsheet_id}/append")
def append_data(spreadsheet_id: str, data: AppendData, session_id: str = Depends(require_session)):
    """Append rows to a spreadsheet"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return append_rows(credentials, spreadsheet_id, data.range, data.values)


@router.delete("/{spreadsheet_id}/clear")
def clear_data(spreadsheet_id: str, range: str, session_id: str = Depends(require_session)):
    """Clear data from a range"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return clear_range(credentials, spreadsheet_id, range)


@router.post("/")
def create_new_spreadsheet(spreadsheet: SpreadsheetCreate, session_id: str = Depends(require_session)):
    """Create a new spreadsheet"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return create_spreadsheet(credentials, spreadsheet.title, spreadsheet.sheets)


@router.post("/{spreadsheet_id}/sheets")
def add_new_sheet(spreadsheet_id: str, sheet: SheetAdd, session_id: str = Depends(require_session)):
    """Add a new sheet to an existing spreadsheet"""
    credentials = get_credentials(session_id)
    if not credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return add_sheet(credentials, spreadsheet_id, sheet.title)
