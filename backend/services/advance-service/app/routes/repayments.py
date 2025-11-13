"""
Repayment management routes
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import Advance, Repayment
from app.schemas import (
    RepaymentScheduleRequest,
    RepaymentResponse,
    RepaymentStatusUpdate
)


router = APIRouter()


@router.post("", response_model=RepaymentResponse, status_code=201)
async def schedule_repayment(
    request: RepaymentScheduleRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule repayment for an advance

    Repayment is automatically processed on the due date
    """
    user_id = UUID(current_user["user_id"])

    # Get advance
    advance_result = await db.execute(
        select(Advance)
        .where(
            Advance.id == request.advance_id,
            Advance.user_id == user_id
        )
    )

    advance = advance_result.scalar()

    if not advance:
        raise HTTPException(status_code=404, detail="Advance not found")

    if advance.status != "disbursed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot schedule repayment for advance with status: {advance.status}"
        )

    if advance.repayment_status in ["completed", "scheduled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Repayment already {advance.repayment_status}"
        )

    # Create repayment schedule
    repayment = Repayment(
        advance_id=request.advance_id,
        user_id=user_id,
        amount=advance.total_amount,
        status="scheduled",
        scheduled_date=request.scheduled_date,
        payment_method=request.payment_method
    )

    db.add(repayment)

    # Update advance
    advance.repayment_status = "scheduled"
    advance.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(repayment)

    print(f"💳 Repayment scheduled for advance {request.advance_id}")
    print(f"   Amount: ${repayment.amount}")
    print(f"   Date: {request.scheduled_date.date()}")

    return RepaymentResponse(
        id=repayment.id,
        advance_id=repayment.advance_id,
        user_id=repayment.user_id,
        amount=repayment.amount,
        status=repayment.status,
        scheduled_date=repayment.scheduled_date,
        attempted_at=repayment.attempted_at,
        completed_at=repayment.completed_at,
        payment_method=repayment.payment_method,
        transaction_id=repayment.transaction_id,
        failure_reason=repayment.failure_reason,
        retry_count=repayment.retry_count,
        created_at=repayment.created_at
    )


@router.get("")
async def get_repayments(
    advance_id: UUID = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get repayment history"""
    user_id = UUID(current_user["user_id"])

    query = select(Repayment).where(Repayment.user_id == user_id)

    if advance_id:
        query = query.where(Repayment.advance_id == advance_id)

    query = query.order_by(Repayment.created_at.desc())

    result = await db.execute(query)
    repayments = result.scalars().all()

    return {
        "repayments": [
            {
                "id": str(rep.id),
                "advance_id": str(rep.advance_id),
                "amount": float(rep.amount),
                "status": rep.status,
                "scheduled_date": rep.scheduled_date.isoformat(),
                "completed_at": rep.completed_at.isoformat() if rep.completed_at else None,
                "payment_method": rep.payment_method,
                "transaction_id": rep.transaction_id,
                "failure_reason": rep.failure_reason,
                "retry_count": rep.retry_count
            }
            for rep in repayments
        ],
        "total": len(repayments)
    }


@router.get("/{repayment_id}", response_model=RepaymentResponse)
async def get_repayment(
    repayment_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific repayment"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(Repayment)
        .where(
            Repayment.id == repayment_id,
            Repayment.user_id == user_id
        )
    )

    repayment = result.scalar()

    if not repayment:
        raise HTTPException(status_code=404, detail="Repayment not found")

    return RepaymentResponse(
        id=repayment.id,
        advance_id=repayment.advance_id,
        user_id=repayment.user_id,
        amount=repayment.amount,
        status=repayment.status,
        scheduled_date=repayment.scheduled_date,
        attempted_at=repayment.attempted_at,
        completed_at=repayment.completed_at,
        payment_method=repayment.payment_method,
        transaction_id=repayment.transaction_id,
        failure_reason=repayment.failure_reason,
        retry_count=repayment.retry_count,
        created_at=repayment.created_at
    )


@router.patch("/{repayment_id}/status")
async def update_repayment_status(
    repayment_id: UUID,
    update: RepaymentStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update repayment status (admin/system endpoint)

    Used by payment processor to update status after processing
    """
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(Repayment)
        .where(
            Repayment.id == repayment_id,
            Repayment.user_id == user_id
        )
    )

    repayment = result.scalar()

    if not repayment:
        raise HTTPException(status_code=404, detail="Repayment not found")

    # Update repayment
    repayment.status = update.status
    repayment.updated_at = datetime.utcnow()

    if update.status == "completed":
        repayment.completed_at = datetime.utcnow()
        repayment.transaction_id = update.transaction_id

        # Update advance
        advance_result = await db.execute(
            select(Advance).where(Advance.id == repayment.advance_id)
        )
        advance = advance_result.scalar()

        if advance:
            advance.status = "repaid"
            advance.repayment_status = "completed"
            advance.repaid_at = datetime.utcnow()
            advance.updated_at = datetime.utcnow()

    elif update.status == "failed":
        repayment.failure_reason = update.failure_reason
        repayment.retry_count += 1

        # Update advance
        advance_result = await db.execute(
            select(Advance).where(Advance.id == repayment.advance_id)
        )
        advance = advance_result.scalar()

        if advance:
            advance.repayment_attempts += 1
            advance.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "message": f"Repayment status updated to {update.status}",
        "repayment_id": str(repayment.id)
    }


@router.post("/{repayment_id}/retry")
async def retry_repayment(
    repayment_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed repayment"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(Repayment)
        .where(
            Repayment.id == repayment_id,
            Repayment.user_id == user_id
        )
    )

    repayment = result.scalar()

    if not repayment:
        raise HTTPException(status_code=404, detail="Repayment not found")

    if repayment.status != "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry repayment with status: {repayment.status}"
        )

    if repayment.retry_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum retry attempts reached. Please contact support."
        )

    # Reset to scheduled for retry
    repayment.status = "scheduled"
    repayment.failure_reason = None
    repayment.updated_at = datetime.utcnow()

    await db.commit()

    # In production, trigger repayment processor
    print(f"🔄 Retrying repayment {repayment_id}")

    return {
        "message": "Repayment retry scheduled",
        "repayment_id": str(repayment.id),
        "retry_count": repayment.retry_count
    }
