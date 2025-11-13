"""
Business intelligence routes
Admin/internal endpoints for business metrics
"""
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import BusinessMetrics
from app.schemas import (
    BusinessMetricsSummary,
    GrowthMetrics,
    RevenueMetrics,
    CohortAnalysis
)


router = APIRouter()


@router.get("/metrics", response_model=BusinessMetricsSummary)
async def get_business_metrics(
    metrics_date: date = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get business metrics summary

    **Note:** In production, this would be admin-only
    Returns aggregate platform metrics
    """
    if not metrics_date:
        metrics_date = date.today()

    # Get or create business metrics
    result = await db.execute(
        select(BusinessMetrics)
        .where(BusinessMetrics.period_date == metrics_date)
    )

    metrics = result.scalar()

    if not metrics:
        metrics = await _generate_mock_business_metrics(metrics_date, db)

    return BusinessMetricsSummary(
        total_users=metrics.total_users,
        new_users=metrics.new_users,
        active_users=metrics.active_users,
        churned_users=metrics.churned_users,
        free_tier_users=metrics.free_tier_users,
        plus_tier_users=metrics.plus_tier_users,
        builder_tier_users=metrics.builder_tier_users,
        mrr=metrics.mrr,
        arr=metrics.arr,
        average_sessions_per_user=metrics.average_sessions_per_user or Decimal("0"),
        average_session_duration=metrics.average_session_duration or 0,
        total_advances_issued=metrics.total_advances_issued,
        total_advance_amount=metrics.total_advance_amount,
        credit_builder_cards_active=metrics.credit_builder_cards_active,
        period_date=metrics.period_date
    )


@router.get("/growth")
async def get_growth_metrics(
    days: int = 30,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user growth metrics over time

    Shows daily/weekly growth trends
    """
    growth_data = []
    today = date.today()

    for i in range(days):
        day = today - timedelta(days=(days - i - 1))

        # Mock growth data
        total = 10000 + (i * 50) + random.randint(-20, 50)
        new = random.randint(30, 100)
        active = int(total * random.uniform(0.6, 0.8))
        growth_rate = (new / total * 100) if total > 0 else Decimal("0")

        growth_data.append(GrowthMetrics(
            date=day,
            total_users=total,
            new_users=new,
            active_users=active,
            growth_rate=Decimal(str(round(growth_rate, 2)))
        ))

    return {
        "period_days": days,
        "growth_metrics": growth_data,
        "total_new_users": sum(g.new_users for g in growth_data),
        "average_daily_growth": sum(g.new_users for g in growth_data) / days
    }


@router.get("/revenue")
async def get_revenue_metrics(
    months: int = 12,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get revenue metrics over time

    Shows MRR, ARR, ARPU trends
    """
    revenue_data = []
    today = date.today()

    for i in range(months):
        month_date = today - timedelta(days=30 * (months - i - 1))

        # Mock revenue data
        mrr = Decimal(str(random.randint(50000, 100000)))
        arr = mrr * 12
        total_users = 10000 + (i * 500)
        arpu = mrr / total_users if total_users > 0 else Decimal("0")
        conversion_rate = Decimal(str(random.uniform(12, 18)))

        revenue_data.append(RevenueMetrics(
            date=month_date,
            mrr=mrr,
            arr=arr,
            arpu=arpu,
            conversion_rate=conversion_rate
        ))

    return {
        "period_months": months,
        "revenue_metrics": revenue_data,
        "latest_mrr": float(revenue_data[-1].mrr),
        "latest_arr": float(revenue_data[-1].arr),
        "mrr_growth": float(revenue_data[-1].mrr - revenue_data[0].mrr)
    }


@router.get("/cohorts")
async def get_cohort_analysis(
    months: int = 6,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user cohort retention analysis

    Shows how well cohorts retain over time
    """
    cohorts = []
    today = date.today()

    for i in range(months):
        cohort_date = today - timedelta(days=30 * (months - i - 1))
        cohort_month = cohort_date.strftime("%Y-%m")
        cohort_size = random.randint(800, 1500)

        # Generate retention rates
        retention_rates = {}
        retention = 100.0

        for month_num in range(1, min(i + 2, 7)):  # Up to 6 months retention
            retention *= random.uniform(0.75, 0.90)  # 75-90% retention each month
            retention_rates[f"month_{month_num}"] = Decimal(str(round(retention, 1)))

        cohorts.append(CohortAnalysis(
            cohort_month=cohort_month,
            cohort_size=cohort_size,
            retention_rates=retention_rates
        ))

    return {
        "period_months": months,
        "cohorts": cohorts,
        "average_month_1_retention": sum(
            c.retention_rates.get("month_1", Decimal("0"))
            for c in cohorts
        ) / len(cohorts)
    }


@router.get("/engagement")
async def get_engagement_metrics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get platform engagement metrics

    Shows how users are engaging with features
    """
    return {
        "daily_active_users": random.randint(6000, 8000),
        "weekly_active_users": random.randint(12000, 15000),
        "monthly_active_users": random.randint(18000, 22000),
        "dau_mau_ratio": round(random.uniform(0.35, 0.45), 2),
        "average_session_duration_minutes": random.randint(8, 15),
        "sessions_per_user": round(random.uniform(3.5, 5.5), 1),
        "feature_adoption": {
            "chat": {"users": 18500, "adoption_rate": 92.5},
            "budgets": {"users": 15200, "adoption_rate": 76.0},
            "savings": {"users": 12800, "adoption_rate": 64.0},
            "advances": {"users": 4200, "adoption_rate": 21.0},
            "credit_builder": {"users": 3800, "adoption_rate": 19.0}
        },
        "top_actions": [
            {"action": "view_transactions", "count": 125000},
            {"action": "send_chat_message", "count": 98000},
            {"action": "check_budget", "count": 75000},
            {"action": "view_savings", "count": 52000},
            {"action": "check_credit_score", "count": 28000}
        ]
    }


@router.get("/product-usage")
async def get_product_usage(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get product usage statistics

    Shows adoption of different financial products
    """
    return {
        "cash_advances": {
            "total_users": random.randint(3800, 4500),
            "active_this_month": random.randint(1200, 1800),
            "total_issued": random.randint(8500, 12000),
            "total_volume": random.randint(850000, 1200000),
            "average_amount": random.randint(120, 180),
            "repayment_rate": round(random.uniform(94, 98), 1)
        },
        "credit_builder": {
            "total_cards": random.randint(3200, 4000),
            "active_cards": random.randint(2800, 3600),
            "total_payments": random.randint(15000, 20000),
            "on_time_payment_rate": round(random.uniform(92, 96), 1),
            "average_credit_limit": random.randint(450, 650),
            "average_score_improvement": random.randint(35, 55)
        },
        "savings_goals": {
            "total_goals": random.randint(12000, 16000),
            "active_goals": random.randint(8500, 12000),
            "completed_goals": random.randint(2800, 4200),
            "total_saved": random.randint(4200000, 5800000),
            "average_goal_amount": random.randint(800, 1500),
            "completion_rate": round(random.uniform(28, 35), 1)
        },
        "budgets": {
            "total_budgets": random.randint(14000, 18000),
            "active_budgets": random.randint(11000, 15000),
            "average_categories": round(random.uniform(4.5, 6.2), 1),
            "average_adherence_rate": round(random.uniform(72, 82), 1)
        }
    }


@router.get("/subscription-metrics")
async def get_subscription_metrics(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get subscription tier metrics

    Shows distribution and conversion rates
    """
    free_users = random.randint(15000, 18000)
    plus_users = random.randint(3000, 4000)
    builder_users = random.randint(2000, 3000)
    total_users = free_users + plus_users + builder_users

    return {
        "total_users": total_users,
        "free_tier": {
            "count": free_users,
            "percentage": round(free_users / total_users * 100, 1)
        },
        "plus_tier": {
            "count": plus_users,
            "percentage": round(plus_users / total_users * 100, 1),
            "price": 5.99,
            "mrr": round(plus_users * 5.99, 2)
        },
        "builder_tier": {
            "count": builder_users,
            "percentage": round(builder_users / total_users * 100, 1),
            "price": 14.99,
            "mrr": round(builder_users * 14.99, 2)
        },
        "conversion_rate": {
            "free_to_paid": round((plus_users + builder_users) / total_users * 100, 1),
            "plus_to_builder": round(builder_users / (plus_users + builder_users) * 100, 1)
        },
        "churn_rate": {
            "plus": round(random.uniform(3, 6), 1),
            "builder": round(random.uniform(2, 4), 1)
        },
        "ltv": {
            "plus": round(random.uniform(120, 180), 2),
            "builder": round(random.uniform(280, 420), 2)
        }
    }


# Helper functions
async def _generate_mock_business_metrics(
    metrics_date: date,
    db: AsyncSession
) -> BusinessMetrics:
    """Generate mock business metrics for development"""

    total_users = random.randint(18000, 22000)
    free_users = int(total_users * random.uniform(0.72, 0.78))
    plus_users = int(total_users * random.uniform(0.12, 0.16))
    builder_users = total_users - free_users - plus_users

    mrr = Decimal(str((plus_users * 5.99) + (builder_users * 14.99)))

    metrics = BusinessMetrics(
        total_users=total_users,
        new_users=random.randint(80, 150),
        active_users=int(total_users * random.uniform(0.65, 0.75)),
        churned_users=random.randint(20, 50),
        free_tier_users=free_users,
        plus_tier_users=plus_users,
        builder_tier_users=builder_users,
        mrr=mrr,
        arr=mrr * 12,
        average_sessions_per_user=Decimal(str(random.uniform(4.0, 6.0))),
        average_session_duration=random.randint(420, 780),  # 7-13 minutes
        total_advances_issued=random.randint(1200, 1800),
        total_advance_amount=Decimal(str(random.randint(180000, 270000))),
        credit_builder_cards_active=random.randint(2800, 3600),
        period_date=metrics_date
    )

    db.add(metrics)
    await db.commit()
    await db.refresh(metrics)

    return metrics
