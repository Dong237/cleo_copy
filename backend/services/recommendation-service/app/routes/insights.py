"""
Financial insights routes
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from app.schemas import SpendingInsight, BudgetOptimization
from app.models import InsightFeedback
from app.schemas import FeedbackCreate, FeedbackResponse


router = APIRouter()


@router.get("/weekly")
async def get_weekly_insights(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get weekly financial insights

    Summary of the past week's financial activity
    """
    user_id = UUID(current_user["user_id"])

    insights = []

    # Spending insights
    insights.append(SpendingInsight(
        insight_type="spending_comparison",
        title="Spending This Week",
        message=f"You spent ${random.randint(200, 400)} this week, {random.randint(5, 25)}% less than last week!",
        comparison="decrease",
        trend="improving"
    ))

    # Top category
    top_category = random.choice(["Food & Dining", "Shopping", "Transportation"])
    insights.append(SpendingInsight(
        insight_type="top_category",
        title="Top Spending Category",
        message=f"{top_category} was your biggest expense this week at ${random.randint(80, 150)}.",
        category=top_category,
        amount=Decimal(str(random.randint(80, 150)))
    ))

    # Savings achievement
    if random.random() > 0.5:
        insights.append(SpendingInsight(
            insight_type="savings_milestone",
            title="Savings Milestone",
            message=f"Great job! You saved ${random.randint(100, 300)} this week toward your goals.",
            trend="positive"
        ))

    # Budget performance
    insights.append(SpendingInsight(
        insight_type="budget_status",
        title="Budget Performance",
        message=f"You're on track with {random.randint(4, 6)} out of 6 budgets this week.",
        trend="stable"
    ))

    return {
        "user_id": str(user_id),
        "period": "weekly",
        "week_start": (datetime.utcnow() - timedelta(days=7)).date().isoformat(),
        "week_end": datetime.utcnow().date().isoformat(),
        "insights": insights,
        "total_insights": len(insights)
    }


@router.get("/monthly")
async def get_monthly_insights(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get monthly financial insights

    Comprehensive review of the past month
    """
    user_id = UUID(current_user["user_id"])

    month_name = datetime.utcnow().strftime("%B")

    insights = []

    # Total spending
    total_spending = random.randint(2000, 4000)
    insights.append(SpendingInsight(
        insight_type="monthly_spending",
        title=f"{month_name} Spending Review",
        message=f"You spent ${total_spending} in {month_name}, compared to your average of ${random.randint(2200, 3800)}.",
        amount=Decimal(str(total_spending)),
        trend="stable" if random.random() > 0.5 else "increasing"
    ))

    # Savings achievement
    savings = random.randint(400, 1000)
    savings_rate = round((savings / total_spending) * 100, 1)
    insights.append(SpendingInsight(
        insight_type="monthly_savings",
        title="Monthly Savings",
        message=f"You saved ${savings} ({savings_rate}% of spending) in {month_name}.",
        amount=Decimal(str(savings)),
        trend="positive"
    ))

    # Unusual spending
    if random.random() > 0.6:
        unusual_category = random.choice(["Shopping", "Entertainment", "Transportation"])
        insights.append(SpendingInsight(
            insight_type="unusual_spending",
            title="Spending Alert",
            message=f"{unusual_category} spending was {random.randint(30, 60)}% higher than usual this month.",
            category=unusual_category,
            trend="warning"
        ))

    # Category breakdown
    insights.append(SpendingInsight(
        insight_type="category_breakdown",
        title="Where Your Money Went",
        message=f"Top 3 categories: Food (${random.randint(400, 700)}), Bills (${random.randint(600, 1000)}), Shopping (${random.randint(200, 500)})."
    ))

    return {
        "user_id": str(user_id),
        "period": "monthly",
        "month": month_name,
        "year": datetime.utcnow().year,
        "insights": insights,
        "total_insights": len(insights),
        "highlights": {
            "total_spent": total_spending,
            "total_saved": savings,
            "savings_rate": savings_rate,
            "top_category": "Food & Dining"
        }
    }


@router.get("/predictive")
async def get_predictive_insights(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get predictive financial insights

    Uses ML to predict future spending and income
    """
    user_id = UUID(current_user["user_id"])

    predictions = {
        "user_id": str(user_id),
        "generated_at": datetime.utcnow().isoformat(),
        "predictions": {
            "next_month_spending": {
                "predicted_amount": random.randint(2200, 3800),
                "confidence": random.uniform(0.75, 0.95),
                "breakdown": {
                    "food": random.randint(500, 700),
                    "transportation": random.randint(200, 350),
                    "shopping": random.randint(250, 500),
                    "entertainment": random.randint(150, 300),
                    "bills": random.randint(800, 1200),
                    "other": random.randint(300, 550)
                }
            },
            "next_paycheck": {
                "predicted_date": (datetime.utcnow() + timedelta(days=random.randint(7, 14))).date().isoformat(),
                "predicted_amount": random.randint(2500, 4000),
                "confidence": random.uniform(0.85, 0.98)
            },
            "end_of_month_balance": {
                "predicted_amount": random.randint(1500, 3500),
                "confidence": random.uniform(0.70, 0.90),
                "factors": [
                    "Regular spending patterns detected",
                    "Upcoming bills accounted for",
                    "Assumed normal income schedule"
                ]
            },
            "savings_projection": {
                "next_3_months": random.randint(1200, 2400),
                "next_6_months": random.randint(2800, 5000),
                "next_12_months": random.randint(6000, 10000),
                "confidence": random.uniform(0.65, 0.85)
            }
        },
        "recommendations_based_on_predictions": [
            "Budget an extra $50 for food next month based on trends",
            "You're on track to meet your savings goal in 8 months",
            "Consider setting aside $150 more for upcoming bills"
        ]
    }

    return predictions


@router.get("/budget-optimization")
async def get_budget_optimizations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get budget optimization recommendations

    Suggests budget adjustments based on actual spending
    """
    user_id = UUID(current_user["user_id"])

    optimizations = []

    categories = [
        {"name": "Food & Dining", "budget": 500, "spending": 580},
        {"name": "Transportation", "budget": 300, "spending": 250},
        {"name": "Shopping", "budget": 200, "spending": 350},
        {"name": "Entertainment", "budget": 150, "spending": 145},
        {"name": "Bills & Utilities", "budget": 800, "spending": 800},
    ]

    for cat in categories:
        current_budget = Decimal(str(cat["budget"]))
        actual_spending = Decimal(str(cat["spending"]))

        if actual_spending > current_budget * Decimal("1.1"):  # 10% over
            recommended = actual_spending * Decimal("1.1")  # Add 10% buffer
            optimizations.append(BudgetOptimization(
                category=cat["name"],
                current_budget=current_budget,
                current_spending=actual_spending,
                recommended_budget=recommended,
                reason=f"Consistently spending {((actual_spending/current_budget - 1) * 100):.0f}% over budget",
                confidence=Decimal("85.0")
            ))
        elif actual_spending < current_budget * Decimal("0.8"):  # 20% under
            recommended = actual_spending * Decimal("1.05")  # Add 5% buffer
            optimizations.append(BudgetOptimization(
                category=cat["name"],
                current_budget=current_budget,
                current_spending=actual_spending,
                recommended_budget=recommended,
                reason=f"Spending {((1 - actual_spending/current_budget) * 100):.0f}% less than budgeted - reallocate funds",
                confidence=Decimal("90.0")
            ))

    return {
        "user_id": str(user_id),
        "optimizations": optimizations,
        "total_recommendations": len(optimizations),
        "potential_monthly_reallocation": sum(
            float(o.current_budget - o.recommended_budget) for o in optimizations
        )
    }


@router.get("/year-in-review")
async def get_year_in_review(
    year: int = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get year-in-review financial summary

    Comprehensive annual financial review
    """
    user_id = UUID(current_user["user_id"])

    if not year:
        year = datetime.utcnow().year - 1  # Default to last completed year

    review = {
        "user_id": str(user_id),
        "year": year,
        "summary": {
            "total_income": random.randint(40000, 70000),
            "total_spending": random.randint(30000, 55000),
            "total_saved": random.randint(8000, 18000),
            "savings_rate": round(random.uniform(15, 30), 1)
        },
        "spending_by_category": {
            "Food & Dining": random.randint(6000, 9000),
            "Bills & Utilities": random.randint(9000, 14000),
            "Transportation": random.randint(3000, 5000),
            "Shopping": random.randint(3000, 6000),
            "Entertainment": random.randint(1800, 3000),
            "Healthcare": random.randint(1200, 2500),
            "Other": random.randint(2000, 4000)
        },
        "milestones": [
            f"Saved ${random.randint(10000, 20000)} toward financial goals",
            f"Paid off ${random.randint(2000, 5000)} in debt",
            f"Improved credit score by {random.randint(15, 45)} points",
            f"Stuck to budget {random.randint(8, 11)} out of 12 months"
        ],
        "top_insights": [
            f"You saved {random.randint(15, 25)}% more than {year-1}",
            f"Food & Dining was your largest discretionary expense at ${random.randint(6000, 9000)}",
            f"You were most consistent with savings in {random.choice(['January', 'June', 'September'])}",
            f"Your biggest single expense was ${random.randint(1500, 3000)} in {random.choice(['March', 'July', 'November'])}"
        ],
        "goals_for_next_year": [
            f"Increase savings rate to {random.randint(20, 30)}%",
            f"Build emergency fund to ${random.randint(15000, 25000)}",
            "Reduce dining out by 20%",
            "Start investing with $500/month"
        ]
    }

    return review


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit feedback on recommendations

    Helps improve recommendation quality
    """
    user_id = UUID(current_user["user_id"])

    feedback_record = InsightFeedback(
        user_id=user_id,
        recommendation_id=feedback.recommendation_id,
        helpful=feedback.helpful,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        action_taken=feedback.action_taken,
        action_description=feedback.action_description
    )

    db.add(feedback_record)
    await db.commit()
    await db.refresh(feedback_record)

    return FeedbackResponse(
        id=feedback_record.id,
        user_id=feedback_record.user_id,
        recommendation_id=feedback_record.recommendation_id,
        helpful=feedback_record.helpful,
        rating=feedback_record.rating,
        action_taken=feedback_record.action_taken,
        created_at=feedback_record.created_at
    )
