"""
Credit score monitoring routes
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from auth import get_current_user
from database import get_db
from app.models import CreditScore, CreditAlert
from app.schemas import (
    CreditScoreResponse,
    CreditScoreHistory,
    CreditScoreFactor,
    CreditAlertResponse
)


router = APIRouter()


@router.get("/score", response_model=CreditScoreResponse)
async def get_current_score(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's current credit score

    In production, this would fetch from credit bureau API (e.g., TransUnion)
    """
    user_id = UUID(current_user["user_id"])

    # Get most recent score
    result = await db.execute(
        select(CreditScore)
        .where(CreditScore.user_id == user_id)
        .order_by(CreditScore.checked_at.desc())
        .limit(1)
    )

    score_record = result.scalar()

    if not score_record:
        # Generate initial mock score for development
        score_record = await _generate_mock_score(user_id, db)

    return CreditScoreResponse(
        id=score_record.id,
        user_id=score_record.user_id,
        score=score_record.score,
        score_provider=score_record.score_provider,
        score_model=score_record.score_model,
        credit_utilization=score_record.credit_utilization,
        payment_history_score=score_record.payment_history_score,
        credit_age_months=score_record.credit_age_months,
        total_accounts=score_record.total_accounts,
        hard_inquiries=score_record.hard_inquiries,
        previous_score=score_record.previous_score,
        score_change=score_record.score_change,
        checked_at=score_record.checked_at
    )


@router.post("/refresh", response_model=CreditScoreResponse)
async def refresh_credit_score(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh credit score from credit bureau

    In production, this would call credit bureau API
    Free tier: Monthly updates
    Plus/Builder tier: Weekly updates
    """
    user_id = UUID(current_user["user_id"])

    # Get most recent score
    result = await db.execute(
        select(CreditScore)
        .where(CreditScore.user_id == user_id)
        .order_by(CreditScore.checked_at.desc())
        .limit(1)
    )

    previous_score_record = result.scalar()

    # Check if user can refresh (rate limiting)
    if previous_score_record:
        time_since_last_check = datetime.utcnow() - previous_score_record.checked_at
        # In production, check user's subscription tier for rate limit
        if time_since_last_check < timedelta(days=7):
            raise HTTPException(
                status_code=429,
                detail=f"Can refresh score once per week. Last check was {time_since_last_check.days} days ago."
            )

    # Generate new mock score (in production, fetch from credit bureau)
    new_score_record = await _generate_mock_score(
        user_id,
        db,
        previous_score_record.score if previous_score_record else None
    )

    # Check for significant changes and create alerts
    if previous_score_record and abs(new_score_record.score_change) >= 10:
        await _create_score_change_alert(
            user_id,
            new_score_record.score,
            new_score_record.score_change,
            db
        )

    return CreditScoreResponse(
        id=new_score_record.id,
        user_id=new_score_record.user_id,
        score=new_score_record.score,
        score_provider=new_score_record.score_provider,
        score_model=new_score_record.score_model,
        credit_utilization=new_score_record.credit_utilization,
        payment_history_score=new_score_record.payment_history_score,
        credit_age_months=new_score_record.credit_age_months,
        total_accounts=new_score_record.total_accounts,
        hard_inquiries=new_score_record.hard_inquiries,
        previous_score=new_score_record.previous_score,
        score_change=new_score_record.score_change,
        checked_at=new_score_record.checked_at
    )


@router.get("/history", response_model=CreditScoreHistory)
async def get_score_history(
    months: int = 12,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get credit score history"""
    user_id = UUID(current_user["user_id"])

    cutoff_date = datetime.utcnow() - timedelta(days=months * 30)

    result = await db.execute(
        select(CreditScore)
        .where(
            CreditScore.user_id == user_id,
            CreditScore.checked_at >= cutoff_date
        )
        .order_by(CreditScore.checked_at.asc())
    )

    scores = result.scalars().all()

    if not scores:
        raise HTTPException(status_code=404, detail="No credit score history found")

    # Calculate statistics
    score_values = [s.score for s in scores]
    current_score = score_values[-1]
    highest = max(score_values)
    lowest = min(score_values)
    average = sum(score_values) // len(score_values)

    # Determine trend
    if len(score_values) >= 2:
        recent_avg = sum(score_values[-3:]) / len(score_values[-3:])
        older_avg = sum(score_values[:3]) / len(score_values[:3]) if len(score_values) >= 6 else score_values[0]

        if recent_avg > older_avg + 5:
            trend = "improving"
        elif recent_avg < older_avg - 5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return CreditScoreHistory(
        scores=[
            CreditScoreResponse(
                id=s.id,
                user_id=s.user_id,
                score=s.score,
                score_provider=s.score_provider,
                score_model=s.score_model,
                credit_utilization=s.credit_utilization,
                payment_history_score=s.payment_history_score,
                credit_age_months=s.credit_age_months,
                total_accounts=s.total_accounts,
                hard_inquiries=s.hard_inquiries,
                previous_score=s.previous_score,
                score_change=s.score_change,
                checked_at=s.checked_at
            )
            for s in scores
        ],
        current_score=current_score,
        highest_score=highest,
        lowest_score=lowest,
        average_score=average,
        trend=trend
    )


@router.get("/factors")
async def get_score_factors(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get factors affecting credit score

    In production, this would analyze credit report data
    """
    user_id = UUID(current_user["user_id"])

    # Get current score
    result = await db.execute(
        select(CreditScore)
        .where(CreditScore.user_id == user_id)
        .order_by(CreditScore.checked_at.desc())
        .limit(1)
    )

    score_record = result.scalar()

    if not score_record:
        raise HTTPException(status_code=404, detail="No credit score found")

    # Generate factors based on score data
    factors = []

    # Credit utilization
    if score_record.credit_utilization:
        util = float(score_record.credit_utilization)
        if util < 30:
            factors.append(CreditScoreFactor(
                factor="Credit Utilization",
                impact="positive",
                description=f"Your credit utilization is {util:.1f}%, which is excellent (under 30%)",
                recommendation="Keep your credit utilization below 30% to maintain a positive impact"
            ))
        elif util < 50:
            factors.append(CreditScoreFactor(
                factor="Credit Utilization",
                impact="neutral",
                description=f"Your credit utilization is {util:.1f}%, which is moderate",
                recommendation="Try to reduce utilization below 30% by paying down balances"
            ))
        else:
            factors.append(CreditScoreFactor(
                factor="Credit Utilization",
                impact="negative",
                description=f"Your credit utilization is {util:.1f}%, which is high (over 50%)",
                recommendation="Pay down credit card balances to reduce utilization below 30%"
            ))

    # Payment history
    if score_record.payment_history_score:
        if score_record.payment_history_score >= 90:
            factors.append(CreditScoreFactor(
                factor="Payment History",
                impact="positive",
                description="Excellent payment history with no missed payments",
                recommendation="Continue making all payments on time"
            ))
        elif score_record.payment_history_score >= 70:
            factors.append(CreditScoreFactor(
                factor="Payment History",
                impact="neutral",
                description="Good payment history with some late payments",
                recommendation="Set up autopay to ensure on-time payments"
            ))
        else:
            factors.append(CreditScoreFactor(
                factor="Payment History",
                impact="negative",
                description="Multiple late or missed payments detected",
                recommendation="Make all payments on time for the next 6 months to improve"
            ))

    # Credit age
    if score_record.credit_age_months:
        if score_record.credit_age_months >= 60:
            factors.append(CreditScoreFactor(
                factor="Credit History Length",
                impact="positive",
                description=f"Strong credit history of {score_record.credit_age_months} months",
                recommendation="Keep old accounts open to maintain history length"
            ))
        elif score_record.credit_age_months >= 24:
            factors.append(CreditScoreFactor(
                factor="Credit History Length",
                impact="neutral",
                description=f"Moderate credit history of {score_record.credit_age_months} months",
                recommendation="Your credit history will continue to strengthen over time"
            ))
        else:
            factors.append(CreditScoreFactor(
                factor="Credit History Length",
                impact="negative",
                description=f"Short credit history of {score_record.credit_age_months} months",
                recommendation="Keep accounts open and active to build history"
            ))

    # Hard inquiries
    if score_record.hard_inquiries is not None:
        if score_record.hard_inquiries == 0:
            factors.append(CreditScoreFactor(
                factor="Credit Inquiries",
                impact="positive",
                description="No recent hard inquiries",
                recommendation="Limit credit applications to minimize hard inquiries"
            ))
        elif score_record.hard_inquiries <= 2:
            factors.append(CreditScoreFactor(
                factor="Credit Inquiries",
                impact="neutral",
                description=f"{score_record.hard_inquiries} recent hard inquiries",
                recommendation="Avoid applying for new credit unless necessary"
            ))
        else:
            factors.append(CreditScoreFactor(
                factor="Credit Inquiries",
                impact="negative",
                description=f"{score_record.hard_inquiries} recent hard inquiries detected",
                recommendation="Avoid new credit applications for the next 6 months"
            ))

    return {
        "factors": factors,
        "total_factors": len(factors)
    }


@router.get("/alerts", response_model=List[CreditAlertResponse])
async def get_alerts(
    unread_only: bool = False,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get credit monitoring alerts"""
    user_id = UUID(current_user["user_id"])

    query = select(CreditAlert).where(CreditAlert.user_id == user_id)

    if unread_only:
        query = query.where(CreditAlert.is_read == False)

    query = query.order_by(CreditAlert.created_at.desc()).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return [
        CreditAlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            title=alert.title,
            message=alert.message,
            alert_data=alert.alert_data,
            is_read=alert.is_read,
            read_at=alert.read_at,
            created_at=alert.created_at
        )
        for alert in alerts
    ]


# Helper functions
async def _generate_mock_score(user_id: UUID, db: AsyncSession, previous_score: int = None) -> CreditScore:
    """Generate mock credit score for development"""

    if previous_score:
        # Simulate small change
        change = random.randint(-15, 20)
        new_score = max(300, min(850, previous_score + change))
    else:
        # Generate initial score (typically 600-750 for new users)
        new_score = random.randint(620, 720)
        change = 0

    score_record = CreditScore(
        user_id=user_id,
        score=new_score,
        score_provider="TransUnion",
        score_model="VantageScore 3.0",
        credit_utilization=Decimal(str(random.uniform(15, 45))),
        payment_history_score=random.randint(75, 100),
        credit_age_months=random.randint(12, 60),
        total_accounts=random.randint(2, 8),
        hard_inquiries=random.randint(0, 3),
        previous_score=previous_score,
        score_change=change,
        checked_at=datetime.utcnow()
    )

    db.add(score_record)
    await db.commit()
    await db.refresh(score_record)

    return score_record


async def _create_score_change_alert(
    user_id: UUID,
    new_score: int,
    change: int,
    db: AsyncSession
):
    """Create alert for significant score change"""

    if change > 0:
        severity = "info"
        title = f"Credit Score Increased by {change} Points!"
        message = f"Your credit score improved to {new_score}. Great work! 🎉"
    else:
        severity = "warning"
        title = f"Credit Score Decreased by {abs(change)} Points"
        message = f"Your credit score dropped to {new_score}. Check your credit report for details."

    alert = CreditAlert(
        user_id=user_id,
        alert_type="score_change",
        severity=severity,
        title=title,
        message=message,
        alert_data={
            "new_score": new_score,
            "change": change
        }
    )

    db.add(alert)
    await db.commit()

    print(f"📊 Credit alert created for user {user_id}: {title}")
