"""
Financial analytics routes
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import FinancialMetrics
from app.schemas import (
    FinancialAnalyticsSummary,
    SpendingBreakdown,
    IncomeVsSpendingTrend
)


router = APIRouter()


@router.get("/summary", response_model=FinancialAnalyticsSummary)
async def get_financial_summary(
    period_days: int = 90,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive financial analytics summary

    Includes:
    - Income and spending totals
    - Spending by category
    - Savings rate
    - Budget adherence
    """
    user_id = UUID(current_user["user_id"])

    period_end = date.today()
    period_start = period_end - timedelta(days=period_days)

    # Get or create financial metrics
    result = await db.execute(
        select(FinancialMetrics)
        .where(
            FinancialMetrics.user_id == user_id,
            FinancialMetrics.period_start == period_start,
            FinancialMetrics.period_end == period_end
        )
    )

    metrics = result.scalar()

    if not metrics:
        metrics = await _generate_mock_financial_metrics(user_id, period_start, period_end, db)

    # Parse spending by category
    spending_breakdown = []
    spending_by_cat = metrics.spending_by_category or {}
    total_spending = metrics.total_spending

    for category, amount in spending_by_cat.items():
        percentage = (Decimal(str(amount)) / total_spending * 100) if total_spending > 0 else Decimal("0")

        # Mock trend
        trend = random.choice(["increasing", "decreasing", "stable"])

        spending_breakdown.append(SpendingBreakdown(
            category=category.title(),
            amount=Decimal(str(amount)),
            percentage=percentage,
            trend=trend
        ))

    # Sort by amount descending
    spending_breakdown.sort(key=lambda x: x.amount, reverse=True)

    # Over budget categories
    over_budget = metrics.over_budget_categories or []

    return FinancialAnalyticsSummary(
        user_id=metrics.user_id,
        total_income=metrics.total_income,
        total_spending=metrics.total_spending,
        total_saved=metrics.total_saved,
        savings_rate=metrics.savings_rate or Decimal("0"),
        average_monthly_income=metrics.average_monthly_income,
        average_monthly_spending=metrics.average_monthly_spending,
        spending_by_category=spending_breakdown,
        budget_adherence_rate=metrics.budget_adherence_rate or Decimal("80"),
        over_budget_categories=over_budget,
        period_start=metrics.period_start,
        period_end=metrics.period_end
    )


@router.get("/income-vs-spending")
async def get_income_vs_spending_trend(
    months: int = 6,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get income vs spending trend over time

    Shows monthly comparison for visual charts
    """
    user_id = UUID(current_user["user_id"])

    # Generate mock monthly data
    trends = []
    today = date.today()

    for i in range(months):
        # Calculate month
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%Y-%m")

        # Mock values
        income = Decimal(str(random.randint(2500, 4000)))
        spending = Decimal(str(random.randint(1800, 3500)))
        savings = income - spending
        savings_rate = (savings / income * 100) if income > 0 else Decimal("0")

        trends.append(IncomeVsSpendingTrend(
            month=month_str,
            income=income,
            spending=spending,
            savings=max(savings, Decimal("0")),
            savings_rate=max(savings_rate, Decimal("0"))
        ))

    # Reverse to chronological order
    trends.reverse()

    return {
        "user_id": str(user_id),
        "months": months,
        "trends": trends,
        "average_savings_rate": sum(t.savings_rate for t in trends) / len(trends)
    }


@router.get("/spending-trends")
async def get_spending_trends(
    category: str = None,
    months: int = 6,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get spending trends by category over time

    Useful for understanding spending patterns
    """
    user_id = UUID(current_user["user_id"])

    categories = [
        "Food & Dining",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Other"
    ] if not category else [category]

    trends_by_category = {}

    for cat in categories:
        monthly_data = []
        today = date.today()

        for i in range(months):
            month_date = today - timedelta(days=30 * i)
            month_str = month_date.strftime("%Y-%m")

            # Mock spending for this category
            amount = Decimal(str(random.randint(100, 800)))

            monthly_data.append({
                "month": month_str,
                "amount": float(amount)
            })

        monthly_data.reverse()
        trends_by_category[cat] = monthly_data

    return {
        "user_id": str(user_id),
        "months": months,
        "trends_by_category": trends_by_category
    }


@router.get("/savings-progress")
async def get_savings_progress(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get savings progress over time

    Shows accumulation of savings
    """
    user_id = UUID(current_user["user_id"])

    # Generate mock savings progression
    months = 12
    today = date.today()
    progress = []

    cumulative = Decimal("0")

    for i in range(months):
        month_date = today - timedelta(days=30 * (months - i - 1))
        month_str = month_date.strftime("%Y-%m")

        # Mock monthly savings
        monthly_savings = Decimal(str(random.randint(200, 800)))
        cumulative += monthly_savings

        progress.append({
            "month": month_str,
            "monthly_savings": float(monthly_savings),
            "cumulative_savings": float(cumulative)
        })

    return {
        "user_id": str(user_id),
        "savings_progress": progress,
        "total_saved": float(cumulative),
        "average_monthly_savings": float(cumulative / months),
        "best_month": max(progress, key=lambda x: x["monthly_savings"])
    }


@router.get("/budget-performance")
async def get_budget_performance(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get budget performance analysis

    Shows how well user is sticking to budgets
    """
    user_id = UUID(current_user["user_id"])

    # Mock budget performance by category
    categories = [
        {"name": "Food & Dining", "budget": 500, "spent": 480, "status": "on_track"},
        {"name": "Transportation", "budget": 200, "spent": 220, "status": "over"},
        {"name": "Shopping", "budget": 300, "spent": 150, "status": "under"},
        {"name": "Entertainment", "budget": 150, "spent": 145, "status": "on_track"},
        {"name": "Bills & Utilities", "budget": 800, "spent": 800, "status": "on_track"}
    ]

    total_budget = sum(c["budget"] for c in categories)
    total_spent = sum(c["spent"] for c in categories)
    adherence_rate = (1 - abs(total_spent - total_budget) / total_budget) * 100

    return {
        "user_id": str(user_id),
        "overall_adherence_rate": round(adherence_rate, 2),
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": total_budget - total_spent,
        "categories": categories,
        "on_track_count": sum(1 for c in categories if c["status"] == "on_track"),
        "over_budget_count": sum(1 for c in categories if c["status"] == "over")
    }


@router.get("/financial-health-score")
async def get_financial_health_score(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate comprehensive financial health score (0-100)

    Factors:
    - Savings rate (30%)
    - Budget adherence (25%)
    - Debt-to-income ratio (20%)
    - Emergency fund coverage (15%)
    - Credit score improvement (10%)
    """
    user_id = UUID(current_user["user_id"])

    # Mock component scores
    savings_rate_score = random.randint(60, 95)
    budget_adherence_score = random.randint(70, 95)
    debt_ratio_score = random.randint(50, 90)
    emergency_fund_score = random.randint(40, 80)
    credit_improvement_score = random.randint(60, 100)

    # Weighted score
    overall_score = (
        savings_rate_score * 0.30 +
        budget_adherence_score * 0.25 +
        debt_ratio_score * 0.20 +
        emergency_fund_score * 0.15 +
        credit_improvement_score * 0.10
    )

    # Determine grade
    if overall_score >= 90:
        grade = "A"
        message = "Excellent! Your financial health is outstanding."
    elif overall_score >= 80:
        grade = "B"
        message = "Great! You're managing your finances well."
    elif overall_score >= 70:
        grade = "C"
        message = "Good! There's room for improvement."
    elif overall_score >= 60:
        grade = "D"
        message = "Fair. Focus on building better habits."
    else:
        grade = "F"
        message = "Needs attention. Let's work on improving your financial health."

    return {
        "user_id": str(user_id),
        "overall_score": round(overall_score, 1),
        "grade": grade,
        "message": message,
        "components": {
            "savings_rate": {
                "score": savings_rate_score,
                "weight": 30,
                "status": "good" if savings_rate_score >= 70 else "needs_improvement"
            },
            "budget_adherence": {
                "score": budget_adherence_score,
                "weight": 25,
                "status": "good" if budget_adherence_score >= 70 else "needs_improvement"
            },
            "debt_ratio": {
                "score": debt_ratio_score,
                "weight": 20,
                "status": "good" if debt_ratio_score >= 70 else "needs_improvement"
            },
            "emergency_fund": {
                "score": emergency_fund_score,
                "weight": 15,
                "status": "good" if emergency_fund_score >= 70 else "needs_improvement"
            },
            "credit_improvement": {
                "score": credit_improvement_score,
                "weight": 10,
                "status": "good" if credit_improvement_score >= 70 else "needs_improvement"
            }
        },
        "recommendations": [
            "Increase your monthly savings by 5%",
            "Review and adjust budget for overspent categories",
            "Build emergency fund to cover 3-6 months expenses"
        ]
    }


# Helper functions
async def _generate_mock_financial_metrics(
    user_id: UUID,
    period_start: date,
    period_end: date,
    db: AsyncSession
) -> FinancialMetrics:
    """Generate mock financial metrics for development"""

    # Mock spending by category
    spending_by_category = {
        "food": random.randint(400, 800),
        "transportation": random.randint(150, 400),
        "shopping": random.randint(200, 600),
        "entertainment": random.randint(100, 300),
        "bills": random.randint(600, 1200),
        "healthcare": random.randint(50, 300),
        "other": random.randint(100, 400)
    }

    total_spending = Decimal(str(sum(spending_by_category.values())))
    total_income = Decimal(str(random.randint(3000, 6000)))
    total_saved = total_income - total_spending
    savings_rate = (total_saved / total_income * 100) if total_income > 0 else Decimal("0")

    # Calculate monthly averages
    days_in_period = (period_end - period_start).days
    months = days_in_period / 30

    metrics = FinancialMetrics(
        user_id=user_id,
        total_income=total_income,
        average_monthly_income=total_income / Decimal(str(months)),
        total_spending=total_spending,
        average_monthly_spending=total_spending / Decimal(str(months)),
        spending_by_category=spending_by_category,
        total_saved=max(total_saved, Decimal("0")),
        savings_rate=max(savings_rate, Decimal("0")),
        budget_adherence_rate=Decimal(str(random.randint(70, 95))),
        over_budget_categories=["transportation"] if random.random() > 0.5 else [],
        period_start=period_start,
        period_end=period_end
    )

    db.add(metrics)
    await db.commit()
    await db.refresh(metrics)

    return metrics
