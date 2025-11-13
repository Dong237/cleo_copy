"""
Cash advance request and management routes
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import Advance, EligibilityCheck
from app.schemas import (
    AdvanceRequest,
    AdvanceResponse,
    AdvanceDetail,
    AdvanceListResponse
)
from app.underwriting import UnderwritingEngine


router = APIRouter()


@router.post("", response_model=AdvanceResponse, status_code=201)
async def request_advance(
    request: AdvanceRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request a cash advance

    Process:
    1. Validate eligibility
    2. Calculate fees and total amount
    3. Create advance record
    4. Process underwriting
    5. Auto-approve if low risk
    """
    user_id = UUID(current_user["user_id"])

    # Check if user has active advance
    active_result = await db.execute(
        select(Advance)
        .where(
            Advance.user_id == user_id,
            Advance.status.in_(["pending", "approved", "disbursed"])
        )
    )
    if active_result.scalar():
        raise HTTPException(
            status_code=400,
            detail="You already have an active advance. Repay it before requesting another."
        )

    # Validate repayment date
    min_repayment_date = datetime.utcnow() + timedelta(days=1)
    max_repayment_date = datetime.utcnow() + timedelta(days=35)

    if request.repayment_date < min_repayment_date:
        raise HTTPException(
            status_code=400,
            detail="Repayment date must be at least 1 day in the future"
        )

    if request.repayment_date > max_repayment_date:
        raise HTTPException(
            status_code=400,
            detail="Repayment date cannot be more than 35 days in the future"
        )

    # Get latest eligibility check
    eligibility_result = await db.execute(
        select(EligibilityCheck)
        .where(EligibilityCheck.user_id == user_id)
        .order_by(EligibilityCheck.checked_at.desc())
        .limit(1)
    )
    latest_check = eligibility_result.scalar()

    # If no recent check or not eligible, require new check
    if not latest_check or not latest_check.is_eligible:
        raise HTTPException(
            status_code=400,
            detail="Please check your eligibility first at /api/v1/advances/eligibility"
        )

    # Validate amount against max eligible
    if request.amount > latest_check.max_advance_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Requested amount ${request.amount} exceeds your maximum of ${latest_check.max_advance_amount}"
        )

    # Calculate fees
    instant_fee = Decimal("3.99") if request.instant_delivery else Decimal("0.00")
    total_amount = request.amount + instant_fee + request.tip_amount

    # Calculate risk score
    risk_score = UnderwritingEngine.calculate_risk_score(
        has_regular_income=latest_check.has_regular_income,
        avg_balance=latest_check.average_balance,
        has_overdrafts=latest_check.has_recent_overdrafts,
        repayment_success_rate=latest_check.previous_repayment_success_rate or Decimal("100.00")
    )

    # Create advance
    advance = Advance(
        user_id=user_id,
        amount=request.amount,
        status="approved",  # Auto-approve for eligible users
        requested_at=datetime.utcnow(),
        approved_at=datetime.utcnow(),
        repayment_due_date=request.repayment_date,
        instant_delivery_fee=instant_fee,
        tip_amount=request.tip_amount,
        total_amount=total_amount,
        risk_score=risk_score,
        underwriting_notes=f"Auto-approved. Risk score: {risk_score}. Max eligible: ${latest_check.max_advance_amount}"
    )

    db.add(advance)
    await db.commit()
    await db.refresh(advance)

    # In production, trigger disbursement workflow
    # For instant delivery: process immediately
    # For standard delivery: process within 1-2 business days

    print(f"💰 Advance approved for user {user_id}: ${request.amount}")
    print(f"   Delivery: {'Instant' if request.instant_delivery else 'Standard'}")
    print(f"   Due date: {request.repayment_date.date()}")
    print(f"   Total amount: ${total_amount}")

    return AdvanceResponse(
        id=advance.id,
        user_id=advance.user_id,
        amount=advance.amount,
        status=advance.status,
        requested_at=advance.requested_at,
        repayment_due_date=advance.repayment_due_date,
        instant_delivery_fee=advance.instant_delivery_fee,
        tip_amount=advance.tip_amount,
        total_amount=advance.total_amount,
        risk_score=advance.risk_score
    )


@router.get("", response_model=AdvanceListResponse)
async def get_advances(
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's advance history"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(Advance)
        .where(Advance.user_id == user_id)
        .order_by(Advance.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    advances = result.scalars().all()

    # Check for active advance
    active_result = await db.execute(
        select(Advance)
        .where(
            Advance.user_id == user_id,
            Advance.status.in_(["pending", "approved", "disbursed"])
        )
    )
    has_active = active_result.scalar() is not None

    return AdvanceListResponse(
        advances=[
            AdvanceResponse(
                id=adv.id,
                user_id=adv.user_id,
                amount=adv.amount,
                status=adv.status,
                requested_at=adv.requested_at,
                repayment_due_date=adv.repayment_due_date,
                instant_delivery_fee=adv.instant_delivery_fee,
                tip_amount=adv.tip_amount,
                total_amount=adv.total_amount,
                risk_score=adv.risk_score
            )
            for adv in advances
        ],
        total=len(advances),
        has_active_advance=has_active
    )


@router.get("/{advance_id}", response_model=AdvanceDetail)
async def get_advance(
    advance_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific advance"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(Advance)
        .where(
            Advance.id == advance_id,
            Advance.user_id == user_id
        )
    )

    advance = result.scalar()

    if not advance:
        raise HTTPException(status_code=404, detail="Advance not found")

    return AdvanceDetail(
        id=advance.id,
        user_id=advance.user_id,
        amount=advance.amount,
        status=advance.status,
        requested_at=advance.requested_at,
        approved_at=advance.approved_at,
        disbursed_at=advance.disbursed_at,
        repayment_due_date=advance.repayment_due_date,
        repaid_at=advance.repaid_at,
        instant_delivery_fee=advance.instant_delivery_fee,
        tip_amount=advance.tip_amount,
        total_amount=advance.total_amount,
        risk_score=advance.risk_score,
        underwriting_notes=advance.underwriting_notes,
        repayment_status=advance.repayment_status,
        repayment_attempts=advance.repayment_attempts,
        created_at=advance.created_at,
        updated_at=advance.updated_at
    )


@router.post("/{advance_id}/cancel")
async def cancel_advance(
    advance_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending advance"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(Advance)
        .where(
            Advance.id == advance_id,
            Advance.user_id == user_id
        )
    )

    advance = result.scalar()

    if not advance:
        raise HTTPException(status_code=404, detail="Advance not found")

    if advance.status not in ["pending", "approved"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel advance with status: {advance.status}"
        )

    advance.status = "cancelled"
    advance.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "message": "Advance cancelled successfully",
        "advance_id": str(advance.id)
    }
