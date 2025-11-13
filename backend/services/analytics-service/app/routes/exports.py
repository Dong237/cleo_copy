"""
Data export routes
"""
from datetime import datetime, date
from uuid import uuid4, UUID
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from app.schemas import ExportRequest, ExportResponse


router = APIRouter()


@router.post("/create", response_model=ExportResponse)
async def create_export(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create data export

    Allows users to export their financial data
    Supports JSON and CSV formats
    """
    user_id = UUID(current_user["user_id"])

    # Validate date range
    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date"
        )

    # Validate export type
    valid_types = ["user_data", "financial_data", "events"]
    if request.export_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid export_type. Must be one of: {valid_types}"
        )

    # Validate format
    valid_formats = ["json", "csv"]
    if request.format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format. Must be one of: {valid_formats}"
        )

    # Create export record (in production, this would queue a background job)
    export_id = uuid4()

    # Mock record count based on export type
    if request.export_type == "user_data":
        record_count = 1  # Single user record
    elif request.export_type == "financial_data":
        days = (request.end_date - request.start_date).days
        record_count = days * 5  # ~5 transactions per day
    else:  # events
        days = (request.end_date - request.start_date).days
        record_count = days * 20  # ~20 events per day

    print(f"📊 Export created: {export_id}")
    print(f"   Type: {request.export_type}")
    print(f"   Format: {request.format}")
    print(f"   Period: {request.start_date} to {request.end_date}")
    print(f"   Records: {record_count}")

    return ExportResponse(
        export_id=export_id,
        export_type=request.export_type,
        format=request.format,
        status="processing",
        record_count=record_count,
        file_size_bytes=None,
        download_url=None,
        created_at=datetime.utcnow()
    )


@router.get("/{export_id}", response_model=ExportResponse)
async def get_export_status(
    export_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get export status

    Check if export is ready for download
    """
    user_id = UUID(current_user["user_id"])

    # In production, query export records from database
    # For now, mock a completed export

    return ExportResponse(
        export_id=export_id,
        export_type="financial_data",
        format="json",
        status="completed",
        record_count=150,
        file_size_bytes=45678,
        download_url=f"https://api.cleo.ai/exports/{export_id}/download",
        created_at=datetime.utcnow()
    )


@router.get("/{export_id}/download")
async def download_export(
    export_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download export file

    Returns the actual export data
    """
    user_id = UUID(current_user["user_id"])

    # In production, stream file from S3 or similar
    # For now, return mock data

    mock_export_data = {
        "export_id": str(export_id),
        "user_id": str(user_id),
        "export_type": "financial_data",
        "exported_at": datetime.utcnow().isoformat(),
        "data": {
            "transactions": [
                {
                    "date": "2025-01-10",
                    "merchant": "Grocery Store",
                    "amount": -125.50,
                    "category": "Food & Dining"
                },
                {
                    "date": "2025-01-09",
                    "merchant": "Gas Station",
                    "amount": -45.00,
                    "category": "Transportation"
                }
            ],
            "budgets": [
                {
                    "category": "Food & Dining",
                    "amount": 500.00,
                    "period": "monthly"
                }
            ],
            "savings_goals": [
                {
                    "name": "Emergency Fund",
                    "target": 5000.00,
                    "current": 2500.00
                }
            ]
        },
        "metadata": {
            "record_count": 2,
            "format": "json"
        }
    }

    return mock_export_data


@router.get("")
async def list_exports(
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's export history

    Shows all past exports
    """
    user_id = UUID(current_user["user_id"])

    # In production, query from database
    # Mock export history

    exports = [
        {
            "export_id": str(uuid4()),
            "export_type": "financial_data",
            "format": "json",
            "status": "completed",
            "record_count": 150,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "export_id": str(uuid4()),
            "export_type": "user_data",
            "format": "json",
            "status": "completed",
            "record_count": 1,
            "created_at": (datetime.utcnow()).isoformat()
        }
    ]

    return {
        "exports": exports[:limit],
        "total": len(exports)
    }


@router.delete("/{export_id}")
async def delete_export(
    export_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an export

    Removes export file and record
    """
    user_id = UUID(current_user["user_id"])

    # In production, delete from storage and database

    print(f"🗑️  Deleted export: {export_id}")

    return {
        "message": "Export deleted successfully",
        "export_id": str(export_id)
    }
