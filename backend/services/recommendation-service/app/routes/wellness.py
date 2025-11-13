"""
Financial wellness routes
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from app.schemas import FinancialWellnessScore, PersonalizedTip, FinancialGoalRecommendation


router = APIRouter()


@router.get("/score", response_model=FinancialWellnessScore)
async def get_financial_wellness_score(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate comprehensive financial wellness score (0-100)

    Factors:
    - Emergency fund (25%)
    - Debt-to-income ratio (20%)
    - Savings rate (20%)
    - Credit score (15%)
    - Budget adherence (10%)
    - Financial goals progress (10%)
    """
    user_id = UUID(current_user["user_id"])

    # Mock component scores
    emergency_fund_score = random.randint(50, 90)
    debt_ratio_score = random.randint(60, 95)
    savings_rate_score = random.randint(55, 85)
    credit_score_value = random.randint(640, 780)
    credit_score_normalized = min(((credit_score_value - 300) / (850 - 300)) * 100, 100)
    budget_adherence_score = random.randint(70, 95)
    goals_progress_score = random.randint(40, 80)

    # Weighted score
    overall_score = round(
        emergency_fund_score * 0.25 +
        debt_ratio_score * 0.20 +
        savings_rate_score * 0.20 +
        credit_score_normalized * 0.15 +
        budget_adherence_score * 0.10 +
        goals_progress_score * 0.10
    )

    # Determine grade and message
    if overall_score >= 90:
        grade = "A"
        message = "Outstanding! Your financial health is excellent."
    elif overall_score >= 80:
        grade = "B"
        message = "Great job! You're managing your finances well."
    elif overall_score >= 70:
        grade = "C"
        message = "Good progress, but there's room for improvement."
    elif overall_score >= 60:
        grade = "D"
        message = "Fair. Focus on building better financial habits."
    else:
        grade = "F"
        message = "Needs attention. Let's work on improving your financial health."

    # Calculate trend (mock)
    previous_score = overall_score + random.randint(-5, 5)
    if overall_score > previous_score + 2:
        trend = "improving"
    elif overall_score < previous_score - 2:
        trend = "declining"
    else:
        trend = "stable"

    components = {
        "emergency_fund": {
            "score": emergency_fund_score,
            "weight": 25,
            "status": "good" if emergency_fund_score >= 70 else "needs_improvement",
            "description": "3-6 months of expenses saved"
        },
        "debt_ratio": {
            "score": debt_ratio_score,
            "weight": 20,
            "status": "good" if debt_ratio_score >= 70 else "needs_improvement",
            "description": "Debt-to-income ratio"
        },
        "savings_rate": {
            "score": savings_rate_score,
            "weight": 20,
            "status": "good" if savings_rate_score >= 70 else "needs_improvement",
            "description": "Percentage of income saved"
        },
        "credit_score": {
            "score": round(credit_score_normalized),
            "weight": 15,
            "status": "good" if credit_score_normalized >= 70 else "needs_improvement",
            "description": f"Credit score: {credit_score_value}"
        },
        "budget_adherence": {
            "score": budget_adherence_score,
            "weight": 10,
            "status": "good" if budget_adherence_score >= 70 else "needs_improvement",
            "description": "Sticking to budgets"
        },
        "goals_progress": {
            "score": goals_progress_score,
            "weight": 10,
            "status": "good" if goals_progress_score >= 70 else "needs_improvement",
            "description": "Progress toward financial goals"
        }
    }

    recommendations = []
    if emergency_fund_score < 70:
        recommendations.append("Build emergency fund to 3-6 months of expenses")
    if savings_rate_score < 70:
        recommendations.append("Increase savings rate to at least 15-20%")
    if credit_score_normalized < 70:
        recommendations.append("Work on improving credit score")
    if budget_adherence_score < 80:
        recommendations.append("Focus on sticking to your budget")

    if not recommendations:
        recommendations = [
            "Keep up the great work!",
            "Consider increasing savings rate further",
            "Explore investment opportunities"
        ]

    return FinancialWellnessScore(
        overall_score=overall_score,
        grade=grade,
        message=message,
        components=components,
        recommendations=recommendations,
        trend=trend
    )


@router.get("/tips")
async def get_personalized_tips(
    category: str = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized financial tips

    Tips are tailored to user's financial situation and goals
    """
    user_id = UUID(current_user["user_id"])

    tips_library = {
        "saving": [
            PersonalizedTip(
                tip_id="save_01",
                category="saving",
                title="Automate Your Savings",
                content="Set up automatic transfers from checking to savings on payday. You won't miss what you don't see!",
                priority="high",
                estimated_impact="$100-300/month",
                difficulty="easy"
            ),
            PersonalizedTip(
                tip_id="save_02",
                category="saving",
                title="The 52-Week Challenge",
                content="Save $1 in week 1, $2 in week 2, and so on. By week 52, you'll have $1,378 saved!",
                priority="medium",
                estimated_impact="$1,378/year",
                difficulty="easy"
            )
        ],
        "spending": [
            PersonalizedTip(
                tip_id="spend_01",
                category="spending",
                title="The 24-Hour Rule",
                content="Wait 24 hours before making non-essential purchases over $50. You'll avoid many impulse buys!",
                priority="high",
                estimated_impact="20-30% reduction in impulse purchases",
                difficulty="easy"
            ),
            PersonalizedTip(
                tip_id="spend_02",
                category="spending",
                title="Cash Envelope System",
                content="Withdraw weekly spending money in cash. Once it's gone, it's gone. Very effective for controlling spending.",
                priority="medium",
                estimated_impact="15-25% reduction in spending",
                difficulty="medium"
            )
        ],
        "debt": [
            PersonalizedTip(
                tip_id="debt_01",
                category="debt",
                title="Avalanche Method",
                content="Pay off debts from highest to lowest interest rate. Save the most money on interest!",
                priority="high",
                estimated_impact="Significant interest savings",
                difficulty="medium"
            ),
            PersonalizedTip(
                tip_id="debt_02",
                category="debt",
                title="Snowball Method",
                content="Pay off smallest debts first for quick wins. Great for motivation!",
                priority="medium",
                estimated_impact="Faster debt elimination",
                difficulty="easy"
            )
        ],
        "investing": [
            PersonalizedTip(
                tip_id="invest_01",
                category="investing",
                title="Start with Index Funds",
                content="Low-cost index funds offer diversification and historically strong returns. Perfect for beginners!",
                priority="medium",
                estimated_impact="7-10% average annual return",
                difficulty="medium"
            ),
            PersonalizedTip(
                tip_id="invest_02",
                category="investing",
                title="Max Out Your 401(k) Match",
                content="If your employer matches 401(k) contributions, contribute enough to get the full match. It's free money!",
                priority="high",
                estimated_impact="100% return on matched contributions",
                difficulty="easy"
            )
        ]
    }

    if category:
        tips = tips_library.get(category, [])
    else:
        # Return mix of tips from all categories
        tips = []
        for cat_tips in tips_library.values():
            tips.extend(cat_tips[:1])  # One from each category

    return {
        "user_id": str(user_id),
        "tips": tips,
        "total": len(tips)
    }


@router.get("/goals/recommendations")
async def get_financial_goal_recommendations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommended financial goals

    Based on user's age, income, and current financial situation
    """
    user_id = UUID(current_user["user_id"])

    # Mock user data
    monthly_income = random.randint(3000, 6000)
    age = random.randint(25, 45)

    recommendations = []

    # Emergency Fund (always high priority)
    emergency_target = monthly_income * 6
    recommendations.append(FinancialGoalRecommendation(
        goal_type="emergency_fund",
        title="Build Emergency Fund",
        description=f"Save 6 months of expenses (${emergency_target:,}) for financial security.",
        target_amount=Decimal(str(emergency_target)),
        recommended_monthly_contribution=Decimal(str(emergency_target / 12)),
        timeline_months=12,
        priority="high"
    ))

    # Retirement savings (age-dependent priority)
    retirement_priority = "high" if age > 35 else "medium"
    recommendations.append(FinancialGoalRecommendation(
        goal_type="retirement",
        title="Retirement Savings",
        description="Save for retirement through 401(k) or IRA. Start early for compound growth!",
        target_amount=Decimal(str(monthly_income * 12 * (65 - age))),
        recommended_monthly_contribution=Decimal(str(monthly_income * 0.15)),
        timeline_months=(65 - age) * 12,
        priority=retirement_priority
    ))

    # Down payment for home (if younger)
    if age < 40:
        recommendations.append(FinancialGoalRecommendation(
            goal_type="home_down_payment",
            title="Home Down Payment",
            description="Save 20% down payment to avoid PMI and get better rates.",
            target_amount=Decimal("60000.00"),  # 20% of $300k home
            recommended_monthly_contribution=Decimal(str(60000 / 60)),
            timeline_months=60,
            priority="medium"
        ))

    # Vacation fund
    recommendations.append(FinancialGoalRecommendation(
        goal_type="vacation",
        title="Dream Vacation Fund",
        description="Save for that trip you've been dreaming about!",
        target_amount=Decimal("5000.00"),
        recommended_monthly_contribution=Decimal("250.00"),
        timeline_months=20,
        priority="low"
    ))

    return {
        "user_id": str(user_id),
        "recommendations": recommendations,
        "total": len(recommendations),
        "next_milestone": recommendations[0].title
    }


@router.get("/health-check")
async def financial_health_checkup(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive financial health checkup

    Reviews all aspects of financial wellness
    """
    user_id = UUID(current_user["user_id"])

    checkup = {
        "user_id": str(user_id),
        "checkup_date": datetime.utcnow().isoformat(),
        "areas": {
            "emergency_savings": {
                "status": random.choice(["excellent", "good", "needs_work", "critical"]),
                "current": random.randint(2000, 10000),
                "target": 15000,
                "recommendation": "Continue building toward 6-month target"
            },
            "debt": {
                "status": random.choice(["excellent", "good", "needs_work"]),
                "total_debt": random.randint(5000, 30000),
                "debt_to_income": random.uniform(0.2, 0.4),
                "recommendation": "Focus on paying down high-interest debt"
            },
            "credit": {
                "status": random.choice(["excellent", "good", "fair"]),
                "score": random.randint(650, 780),
                "trend": random.choice(["improving", "stable", "declining"]),
                "recommendation": "Keep utilization below 30% and pay on time"
            },
            "savings_rate": {
                "status": random.choice(["excellent", "good", "needs_work"]),
                "current_rate": random.uniform(10, 20),
                "target_rate": 20,
                "recommendation": "Aim for 20% savings rate"
            },
            "insurance": {
                "status": random.choice(["adequate", "needs_review"]),
                "has_health": True,
                "has_life": random.choice([True, False]),
                "has_disability": random.choice([True, False]),
                "recommendation": "Review coverage annually"
            }
        },
        "overall_health": "good",
        "priority_actions": [
            "Increase emergency fund by $200/month",
            "Pay extra $100/month toward highest interest debt",
            "Review and cancel unused subscriptions"
        ]
    }

    return checkup
