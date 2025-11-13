"""
User analytics routes
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from auth import get_current_user
from database import get_db
from app.models import UserAnalytics, EventLog
from app.schemas import (
    UserEngagementMetrics,
    UserFinancialHealth,
    UserAnalyticsSummary
)


router = APIRouter()


@router.get("/engagement", response_model=UserEngagementMetrics)
async def get_user_engagement(
    period_days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user engagement metrics

    Tracks:
    - Session count and duration
    - Feature usage (chat, budgets, savings, advances)
    - Activity patterns
    """
    user_id = UUID(current_user["user_id"])

    # Calculate period
    period_end = date.today()
    period_start = period_end - timedelta(days=period_days)

    # Get or create analytics record
    result = await db.execute(
        select(UserAnalytics)
        .where(
            UserAnalytics.user_id == user_id,
            UserAnalytics.period_start == period_start,
            UserAnalytics.period_end == period_end
        )
    )

    analytics = result.scalar()

    if not analytics:
        # Generate mock data for development
        analytics = await _generate_mock_user_analytics(user_id, period_start, period_end, db)

    return UserEngagementMetrics(
        user_id=analytics.user_id,
        total_sessions=analytics.total_sessions,
        average_session_duration_seconds=analytics.average_session_duration_seconds,
        last_active_at=analytics.last_active_at,
        chat_messages_sent=analytics.chat_messages_sent,
        budgets_created=analytics.budgets_created,
        savings_goals_created=analytics.savings_goals_created,
        advances_requested=analytics.advances_requested
    )


@router.get("/financial-health", response_model=UserFinancialHealth)
async def get_financial_health(
    period_days: int = 90,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user financial health indicators

    Includes:
    - Total saved amount
    - Cash advances taken
    - Credit score improvement
    - Savings rate
    - Budget adherence
    """
    user_id = UUID(current_user["user_id"])

    # In production, aggregate from other services
    # For now, generate mock data

    total_saved = Decimal(str(random.randint(500, 5000)))
    total_advanced = Decimal(str(random.randint(0, 500)))
    credit_improvement = random.randint(-20, 80)

    return UserFinancialHealth(
        user_id=user_id,
        total_saved=total_saved,
        total_advanced=total_advanced,
        credit_score_improvement=credit_improvement,
        savings_rate=Decimal(str(random.randint(5, 25))),
        budget_adherence_rate=Decimal(str(random.randint(60, 95)))
    )


@router.get("/summary", response_model=UserAnalyticsSummary)
async def get_user_analytics_summary(
    period_days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get complete user analytics summary"""
    user_id = UUID(current_user["user_id"])

    period_end = date.today()
    period_start = period_end - timedelta(days=period_days)

    # Get engagement metrics
    result = await db.execute(
        select(UserAnalytics)
        .where(
            UserAnalytics.user_id == user_id,
            UserAnalytics.period_start == period_start,
            UserAnalytics.period_end == period_end
        )
    )

    analytics = result.scalar()

    if not analytics:
        analytics = await _generate_mock_user_analytics(user_id, period_start, period_end, db)

    engagement = UserEngagementMetrics(
        user_id=analytics.user_id,
        total_sessions=analytics.total_sessions,
        average_session_duration_seconds=analytics.average_session_duration_seconds,
        last_active_at=analytics.last_active_at,
        chat_messages_sent=analytics.chat_messages_sent,
        budgets_created=analytics.budgets_created,
        savings_goals_created=analytics.savings_goals_created,
        advances_requested=analytics.advances_requested
    )

    financial_health = UserFinancialHealth(
        user_id=analytics.user_id,
        total_saved=analytics.total_saved,
        total_advanced=analytics.total_advanced,
        credit_score_improvement=analytics.credit_score_improvement
    )

    return UserAnalyticsSummary(
        user_id=user_id,
        engagement=engagement,
        financial_health=financial_health,
        period_start=period_start,
        period_end=period_end
    )


@router.get("/activity-timeline")
async def get_activity_timeline(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user activity timeline

    Shows daily activity breakdown
    """
    user_id = UUID(current_user["user_id"])

    # In production, query event logs
    # For now, generate mock timeline

    timeline = []
    today = date.today()

    for i in range(days):
        day = today - timedelta(days=i)

        # Mock activity
        sessions = random.randint(0, 5)
        events = random.randint(0, 20) if sessions > 0 else 0

        timeline.append({
            "date": day.isoformat(),
            "sessions": sessions,
            "total_events": events,
            "chat_messages": random.randint(0, 10) if sessions > 0 else 0,
            "transactions_viewed": random.randint(0, 15) if sessions > 0 else 0
        })

    return {
        "user_id": str(user_id),
        "period_days": days,
        "timeline": timeline,
        "total_active_days": sum(1 for t in timeline if t["sessions"] > 0)
    }


@router.get("/feature-usage")
async def get_feature_usage(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get feature usage statistics

    Shows which features the user engages with most
    """
    user_id = UUID(current_user["user_id"])

    # In production, aggregate from event logs
    # For now, mock data

    features = [
        {
            "feature": "Chat",
            "usage_count": random.randint(20, 100),
            "last_used": datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
            "engagement_score": random.randint(60, 100)
        },
        {
            "feature": "Budget Tracking",
            "usage_count": random.randint(10, 50),
            "last_used": datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
            "engagement_score": random.randint(50, 90)
        },
        {
            "feature": "Savings Goals",
            "usage_count": random.randint(5, 30),
            "last_used": datetime.utcnow() - timedelta(hours=random.randint(12, 120)),
            "engagement_score": random.randint(40, 80)
        },
        {
            "feature": "Transaction Analysis",
            "usage_count": random.randint(15, 60),
            "last_used": datetime.utcnow() - timedelta(hours=random.randint(6, 96)),
            "engagement_score": random.randint(55, 85)
        },
        {
            "feature": "Credit Score Monitoring",
            "usage_count": random.randint(3, 20),
            "last_used": datetime.utcnow() - timedelta(days=random.randint(1, 7)),
            "engagement_score": random.randint(45, 75)
        }
    ]

    # Sort by usage count
    features.sort(key=lambda x: x["usage_count"], reverse=True)

    return {
        "user_id": str(user_id),
        "features": features,
        "most_used_feature": features[0]["feature"],
        "total_feature_interactions": sum(f["usage_count"] for f in features)
    }


# Helper functions
async def _generate_mock_user_analytics(
    user_id: UUID,
    period_start: date,
    period_end: date,
    db: AsyncSession
) -> UserAnalytics:
    """Generate mock user analytics for development"""

    analytics = UserAnalytics(
        user_id=user_id,
        total_sessions=random.randint(20, 100),
        average_session_duration_seconds=random.randint(180, 900),  # 3-15 minutes
        last_active_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
        chat_messages_sent=random.randint(30, 150),
        budgets_created=random.randint(1, 5),
        savings_goals_created=random.randint(0, 3),
        advances_requested=random.randint(0, 2),
        total_saved=Decimal(str(random.randint(500, 5000))),
        total_advanced=Decimal(str(random.randint(0, 500))),
        credit_score_improvement=random.randint(-10, 50),
        period_start=period_start,
        period_end=period_end
    )

    db.add(analytics)
    await db.commit()
    await db.refresh(analytics)

    return analytics
