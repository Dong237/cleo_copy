"""
Eligibility check routes
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from auth import get_current_user
from database import get_db
from app.models import EligibilityCheck, Advance, Repayment
from app.schemas import EligibilityCheckResponse
from app.underwriting import UnderwritingEngine


router = APIRouter()


@router.get("", response_model=EligibilityCheckResponse)
async def check_eligibility(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user is eligible for a cash advance

    Analyzes:
    - Income history and stability
    - Account balance patterns
    - Overdraft history
    - Previous advance repayment history
    """
    user_id = UUID(current_user["user_id"])

    # Get mock banking data (in production, fetch from Banking Service)
    banking_data = await _get_mock_banking_data(user_id)

    # Get advance history
    advance_history = await _get_advance_history(user_id, db)

    # Run underwriting check
    is_eligible, max_amount, reason, factors = await UnderwritingEngine.check_eligibility(
        user_id,
        banking_data,
        advance_history
    )

    # Save eligibility check
    eligibility_check = EligibilityCheck(
        user_id=user_id,
        is_eligible=is_eligible,
        max_advance_amount=max_amount,
        reason=reason,
        has_regular_income=factors.get("has_regular_income", False),
        income_history_days=factors.get("income_history_days", 0),
        has_recent_overdrafts=factors.get("has_recent_overdrafts", False),
        average_balance=factors.get("average_balance", Decimal("0.00")),
        previous_advance_count=factors.get("previous_advance_count", 0),
        previous_repayment_success_rate=factors.get("previous_repayment_success_rate"),
        checked_at=datetime.utcnow()
    )

    db.add(eligibility_check)
    await db.commit()
    await db.refresh(eligibility_check)

    return EligibilityCheckResponse(
        is_eligible=eligibility_check.is_eligible,
        max_advance_amount=eligibility_check.max_advance_amount,
        reason=eligibility_check.reason,
        check_id=eligibility_check.id,
        has_regular_income=eligibility_check.has_regular_income,
        income_history_days=eligibility_check.income_history_days,
        has_recent_overdrafts=eligibility_check.has_recent_overdrafts,
        average_balance=eligibility_check.average_balance,
        previous_advance_count=eligibility_check.previous_advance_count,
        previous_repayment_success_rate=eligibility_check.previous_repayment_success_rate,
        checked_at=eligibility_check.checked_at
    )


@router.get("/history")
async def get_eligibility_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's eligibility check history"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(EligibilityCheck)
        .where(EligibilityCheck.user_id == user_id)
        .order_by(EligibilityCheck.checked_at.desc())
        .limit(limit)
    )

    checks = result.scalars().all()

    return {
        "checks": [
            {
                "check_id": check.id,
                "is_eligible": check.is_eligible,
                "max_advance_amount": float(check.max_advance_amount),
                "reason": check.reason,
                "checked_at": check.checked_at.isoformat()
            }
            for check in checks
        ],
        "total": len(checks)
    }


async def _get_mock_banking_data(user_id: UUID) -> dict:
    """
    Mock banking data for development

    In production, this would fetch real data from Banking Service API
    """
    now = datetime.utcnow()

    # Mock recent deposits (simulating paycheck)
    recent_deposits = [
        {
            "date": now - timedelta(days=7),
            "amount": Decimal("1500.00"),
            "description": "Payroll Deposit"
        },
        {
            "date": now - timedelta(days=21),
            "amount": Decimal("1500.00"),
            "description": "Payroll Deposit"
        },
        {
            "date": now - timedelta(days=35),
            "amount": Decimal("1500.00"),
            "description": "Payroll Deposit"
        }
    ]

    # Mock transactions (no overdrafts)
    recent_transactions = [
        {
            "date": now - timedelta(days=2),
            "amount": Decimal("-45.00"),
            "description": "Grocery Store"
        },
        {
            "date": now - timedelta(days=5),
            "amount": Decimal("-120.00"),
            "description": "Electric Company"
        }
    ]

    # Mock daily balances
    daily_balances = [
        {
            "date": now - timedelta(days=i),
            "balance": Decimal("800.00") + (Decimal("50.00") * i % 10)
        }
        for i in range(30)
    ]

    return {
        "user_id": user_id,
        "current_balance": Decimal("950.00"),
        "recent_deposits": recent_deposits,
        "recent_transactions": recent_transactions,
        "daily_balances": daily_balances
    }


async def _get_advance_history(user_id: UUID, db: AsyncSession) -> dict:
    """Get user's advance and repayment history"""

    # Get total advances
    total_result = await db.execute(
        select(func.count(Advance.id))
        .where(Advance.user_id == user_id)
    )
    total_advances = total_result.scalar() or 0

    # Check for active advances
    active_result = await db.execute(
        select(Advance)
        .where(
            Advance.user_id == user_id,
            Advance.status.in_(["pending", "approved", "disbursed"])
        )
    )
    has_active_advance = active_result.scalar() is not None

    # Calculate repayment success rate
    if total_advances > 0:
        successful_result = await db.execute(
            select(func.count(Advance.id))
            .where(
                Advance.user_id == user_id,
                Advance.repayment_status == "completed"
            )
        )
        successful_repayments = successful_result.scalar() or 0
        success_rate = Decimal(str((successful_repayments / total_advances) * 100))
    else:
        success_rate = Decimal("100.00")  # No history = perfect score

    return {
        "total_advances": total_advances,
        "has_active_advance": has_active_advance,
        "repayment_success_rate": success_rate
    }
