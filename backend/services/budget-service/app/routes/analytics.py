"""
Budget analytics and insights routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, timedelta
from decimal import Decimal
from typing import List
import random

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user

from app.schemas import (
    BudgetAnalyticsResponse,
    SpendingTrend,
    SpendingComparison,
    BudgetInsight
)
from app.models import Budget

router = APIRouter()


@router.get("/insights", response_model=BudgetAnalyticsResponse)
async def get_budget_analytics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive budget analytics and AI-generated insights
    """
    # Calculate period (current month)
    today = date.today()
    period_start = date(today.year, today.month, 1)
    period_end = today

    # Previous month for comparison
    if today.month == 1:
        prev_month_start = date(today.year - 1, 12, 1)
        prev_month_end = date(today.year - 1, 12, 31)
    else:
        prev_month_start = date(today.year, today.month - 1, 1)
        # Last day of previous month
        prev_month_end = period_start - timedelta(days=1)

    # Generate spending by day (mock data)
    spending_by_day = []
    current_date = period_start
    while current_date <= period_end:
        daily_amount = Decimal(str(round(random.uniform(20, 150), 2)))
        spending_by_day.append(SpendingTrend(
            date=current_date,
            amount=daily_amount
        ))
        current_date += timedelta(days=1)

    # Calculate comparison
    current_spending = sum(day.amount for day in spending_by_day)
    previous_spending = Decimal(str(round(random.uniform(800, 1200), 2)))

    change_amount = current_spending - previous_spending
    change_percentage = float(change_amount / previous_spending * 100) if previous_spending > 0 else 0

    comparison = SpendingComparison(
        current_period=current_spending,
        previous_period=previous_spending,
        change_amount=change_amount,
        change_percentage=round(change_percentage, 2)
    )

    # Generate insights
    insights: List[BudgetInsight] = []

    # Overspending insight
    if change_percentage > 15:
        insights.append(BudgetInsight(
            insight_type="overspending",
            category=None,
            message=f"You're spending {abs(round(change_percentage))}% more than last month",
            severity="warning",
            recommendation="Consider reviewing your discretionary spending and sticking to your budgets"
        ))

    # Underspending insight
    elif change_percentage < -10:
        insights.append(BudgetInsight(
            insight_type="underspending",
            category=None,
            message=f"Great job! You're spending {abs(round(change_percentage))}% less than last month",
            severity="info",
            recommendation="Consider moving the savings into your emergency fund or savings goals"
        ))

    # Weekend spending insight
    insights.append(BudgetInsight(
        insight_type="pattern",
        category="dining",
        message="You tend to spend 40% more on weekends",
        severity="info",
        recommendation="Try meal prepping on Sundays to reduce weekend dining expenses"
    ))

    # Subscription insight
    insights.append(BudgetInsight(
        insight_type="recurring",
        category="subscriptions",
        message="You have 8 active subscriptions totaling $85/month",
        severity="warning",
        recommendation="Review your subscriptions and cancel unused ones to save money"
    ))

    # Top spending categories (mock)
    top_spending_categories = [
        {"category": "Food & Dining", "amount": 450.00, "percentage": 35},
        {"category": "Shopping", "amount": 320.00, "percentage": 25},
        {"category": "Transportation", "amount": 180.00, "percentage": 14},
        {"category": "Entertainment", "amount": 150.00, "percentage": 12},
        {"category": "Bills & Utilities", "amount": 180.00, "percentage": 14}
    ]

    # Calculate budget adherence score
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.user_id == current_user["user_id"],
                Budget.is_active == True,
                Budget.start_date <= period_end,
                Budget.end_date >= period_start
            )
        )
    )
    budgets = result.scalars().all()

    if budgets:
        # Mock adherence - in production, calculate based on actual vs budget
        adherence_scores = [random.uniform(60, 95) for _ in budgets]
        budget_adherence_score = sum(adherence_scores) / len(adherence_scores)
    else:
        budget_adherence_score = 0.0

    return BudgetAnalyticsResponse(
        period_start=period_start,
        period_end=period_end,
        spending_by_day=spending_by_day,
        comparison=comparison,
        insights=insights,
        top_spending_categories=top_spending_categories,
        budget_adherence_score=round(budget_adherence_score, 2)
    )


@router.get("/recommendations")
async def get_budget_recommendations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized budget recommendations based on spending patterns
    """
    # In production, this would analyze spending history and provide ML-based recommendations
    recommendations = [
        {
            "category": "food_dining",
            "current_spending": 450.00,
            "recommended_budget": 350.00,
            "potential_savings": 100.00,
            "reason": "You're spending 28% more than average users in your income bracket"
        },
        {
            "category": "subscriptions",
            "current_spending": 85.00,
            "recommended_budget": 50.00,
            "potential_savings": 35.00,
            "reason": "You have unused subscriptions that can be cancelled"
        },
        {
            "category": "transportation",
            "current_spending": 180.00,
            "recommended_budget": 150.00,
            "potential_savings": 30.00,
            "reason": "Consider using public transit 2 days a week to save on gas"
        }
    ]

    total_potential_savings = sum(r["potential_savings"] for r in recommendations)

    return {
        "recommendations": recommendations,
        "total_potential_savings": total_potential_savings,
        "message": f"You could save ${total_potential_savings:.2f} per month with these recommendations"
    }
