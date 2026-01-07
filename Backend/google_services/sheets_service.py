"""
Google Sheets Service
Integrates with Sheets API for spreadsheet operations
"""
from googleapiclient.discovery import build
from typing import Any, List, Optional, Dict


def get_sheets_service(credentials: Any):
    """Create Google Sheets service instance"""
    return build("sheets", "v4", credentials=credentials)


def get_spreadsheet(credentials: Any, spreadsheet_id: str):
    """Get spreadsheet metadata"""
    service = get_sheets_service(credentials)
    
    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()
    
    return {
        "id": spreadsheet.get("spreadsheetId"),
        "title": spreadsheet.get("properties", {}).get("title"),
        "locale": spreadsheet.get("properties", {}).get("locale"),
        "sheets": [
            {
                "id": sheet.get("properties", {}).get("sheetId"),
                "title": sheet.get("properties", {}).get("title"),
                "index": sheet.get("properties", {}).get("index"),
                "rowCount": sheet.get("properties", {}).get("gridProperties", {}).get("rowCount"),
                "columnCount": sheet.get("properties", {}).get("gridProperties", {}).get("columnCount"),
            }
            for sheet in spreadsheet.get("sheets", [])
        ],
        "url": spreadsheet.get("spreadsheetUrl")
    }


def read_range(credentials: Any, spreadsheet_id: str, range: str):
    """
    Read data from a spreadsheet range
    range examples: "Sheet1!A1:D10", "Sheet1", "A1:B5"
    """
    service = get_sheets_service(credentials)
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range
    ).execute()
    
    return {
        "range": result.get("range"),
        "values": result.get("values", [])
    }


def write_range(credentials: Any, spreadsheet_id: str, range: str, values: List[List]):
    """
    Write data to a spreadsheet range
    values: 2D array like [["A1", "B1"], ["A2", "B2"]]
    """
    service = get_sheets_service(credentials)
    
    body = {"values": values}
    
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    return {
        "updated_range": result.get("updatedRange"),
        "updated_rows": result.get("updatedRows"),
        "updated_columns": result.get("updatedColumns"),
        "updated_cells": result.get("updatedCells")
    }


def append_rows(credentials: Any, spreadsheet_id: str, range: str, values: List[List]):
    """Append rows to a spreadsheet"""
    service = get_sheets_service(credentials)
    
    body = {"values": values}
    
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    
    return {
        "updated_range": result.get("updates", {}).get("updatedRange"),
        "updated_rows": result.get("updates", {}).get("updatedRows"),
        "updated_cells": result.get("updates", {}).get("updatedCells")
    }


def clear_range(credentials: Any, spreadsheet_id: str, range: str):
    """Clear data from a range"""
    service = get_sheets_service(credentials)
    
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range
    ).execute()
    
    return {"message": f"Range {range} cleared successfully"}


def create_spreadsheet(credentials: Any, title: str, sheets: Optional[List[str]] = None):
    """Create a new spreadsheet"""
    service = get_sheets_service(credentials)
    
    spreadsheet_body: Dict[str, Any] = {
        "properties": {"title": title}
    }
    
    if sheets:
        spreadsheet_body["sheets"] = [
            {"properties": {"title": sheet_name}}
            for sheet_name in sheets
        ]
    
    spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
    
    return {
        "id": spreadsheet.get("spreadsheetId"),
        "title": title,
        "url": spreadsheet.get("spreadsheetUrl")
    }


def add_sheet(credentials: Any, spreadsheet_id: str, sheet_title: str):
    """Add a new sheet to an existing spreadsheet"""
    service = get_sheets_service(credentials)
    
    request = {
        "requests": [{
            "addSheet": {
                "properties": {"title": sheet_title}
            }
        }]
    }
    
    result = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request
    ).execute()
    
    return {
        "sheet_id": result.get("replies", [{}])[0].get("addSheet", {}).get("properties", {}).get("sheetId"),
        "title": sheet_title
    }
