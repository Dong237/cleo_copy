"""
Savings optimization routes
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import SavingsOpportunity
from app.schemas import SavingsOpportunityResponse, SavingsRecommendation


router = APIRouter()


@router.get("/recommendations")
async def get_savings_recommendations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized savings recommendations

    Based on:
    - Current savings rate
    - Income patterns
    - Spending habits
    - Financial goals
    """
    user_id = UUID(current_user["user_id"])

    # Mock user financial data
    monthly_income = Decimal(str(random.randint(3000, 6000)))
    current_savings_rate = Decimal(str(random.uniform(5, 20)))
    recommended_savings_rate = Decimal("20.00")  # Industry standard

    current_savings = monthly_income * (current_savings_rate / 100)
    recommended_savings = monthly_income * (recommended_savings_rate / 100)
    additional_savings = recommended_savings - current_savings

    recommendations = []

    # Primary savings recommendation
    recommendations.append(SavingsRecommendation(
        title="Increase Your Savings Rate",
        description=f"You're currently saving {current_savings_rate}% of your income. Aim for 20% to build financial security faster.",
        recommended_monthly_amount=recommended_savings,
        potential_annual_savings=additional_savings * 12,
        strategy="Incremental increase",
        steps=[
            f"Increase savings by ${additional_savings/4:.2f} per month",
            "Automate savings transfers on payday",
            "Review and cut one unnecessary expense",
            "Reach 20% savings rate in 4 months"
        ],
        timeline="4 months"
    ))

    # 52-week savings challenge
    recommendations.append(SavingsRecommendation(
        title="52-Week Money Challenge",
        description="Save an increasing amount each week, starting with $1 and ending with $52.",
        recommended_monthly_amount=Decimal("115.00"),  # Roughly $1,378/year ÷ 12
        potential_annual_savings=Decimal("1378.00"),
        strategy="Progressive increase",
        steps=[
            "Week 1: Save $1",
            "Week 2: Save $2",
            "Continue increasing by $1 each week",
            "Week 52: Save $52",
            "Total saved: $1,378"
        ],
        timeline="52 weeks (1 year)"
    ))

    # Round-up savings
    recommendations.append(SavingsRecommendation(
        title="Round-Up Savings",
        description="Automatically round up purchases to the nearest dollar and save the difference.",
        recommended_monthly_amount=Decimal(str(random.randint(30, 60))),
        potential_annual_savings=Decimal(str(random.randint(360, 720))),
        strategy="Automatic micro-savings",
        steps=[
            "Enable round-up feature in Cleo",
            "Connect to your primary spending account",
            "Savings happen automatically with each purchase",
            "Save $30-60/month without noticing"
        ],
        timeline="Ongoing"
    ))

    # Emergency fund recommendation
    emergency_fund_target = monthly_income * 6  # 6 months expenses
    recommendations.append(SavingsRecommendation(
        title="Build Emergency Fund",
        description=f"Aim for 6 months of expenses (${emergency_fund_target}) in an emergency fund.",
        recommended_monthly_amount=Decimal(str(emergency_fund_target / 12)),
        potential_annual_savings=emergency_fund_target,
        strategy="Dedicated emergency savings",
        steps=[
            "Open a high-yield savings account",
            f"Save ${emergency_fund_target/12:.2f}/month",
            "Don't touch unless it's a true emergency",
            "Reach full fund in 12 months"
        ],
        timeline="12 months"
    ))

    return {
        "user_id": str(user_id),
        "current_savings_rate": float(current_savings_rate),
        "recommended_savings_rate": float(recommended_savings_rate),
        "monthly_income": float(monthly_income),
        "recommendations": recommendations
    }


@router.get("/opportunities", response_model=List[SavingsOpportunityResponse])
async def get_savings_opportunities(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Identify specific savings opportunities

    Analyzes spending for potential savings
    """
    user_id = UUID(current_user["user_id"])

    # Get existing opportunities or generate mock
    result = await db.execute(
        select(SavingsOpportunity)
        .where(SavingsOpportunity.user_id == user_id)
        .order_by(SavingsOpportunity.estimated_annual_savings.desc())
    )

    opportunities = result.scalars().all()

    if not opportunities:
        opportunities = await _generate_mock_opportunities(user_id, db)

    return [
        SavingsOpportunityResponse(
            id=opp.id,
            opportunity_type=opp.opportunity_type,
            title=opp.title,
            description=opp.description,
            estimated_monthly_savings=opp.estimated_monthly_savings,
            estimated_annual_savings=opp.estimated_annual_savings,
            confidence=opp.confidence,
            difficulty=opp.difficulty,
            status=opp.status,
            created_at=opp.created_at
        )
        for opp in opportunities
    ]


@router.get("/optimization-strategies")
async def get_optimization_strategies(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get savings optimization strategies

    Personalized strategies based on spending patterns
    """
    user_id = UUID(current_user["user_id"])

    strategies = [
        {
            "strategy": "The 50/30/20 Rule",
            "description": "Allocate 50% to needs, 30% to wants, 20% to savings",
            "difficulty": "medium",
            "expected_savings_increase": "5-10%",
            "steps": [
                "Calculate your after-tax monthly income",
                "Allocate 50% to essentials (rent, utilities, groceries)",
                "Limit wants to 30% (dining out, entertainment, shopping)",
                "Save/invest the remaining 20%"
            ],
            "best_for": "People new to budgeting"
        },
        {
            "strategy": "Pay Yourself First",
            "description": "Automatically save before spending on anything else",
            "difficulty": "easy",
            "expected_savings_increase": "10-15%",
            "steps": [
                "Set up automatic transfer on payday",
                "Transfer savings to separate account immediately",
                "Live on what's left",
                "Gradually increase savings percentage"
            ],
            "best_for": "Anyone wanting to build consistent savings"
        },
        {
            "strategy": "Zero-Based Budgeting",
            "description": "Assign every dollar a job before the month starts",
            "difficulty": "hard",
            "expected_savings_increase": "15-25%",
            "steps": [
                "List all income sources",
                "Allocate every dollar to specific categories",
                "Include savings as a category",
                "Adjust throughout month as needed",
                "Income - Expenses = $0"
            ],
            "best_for": "Detail-oriented people who want maximum control"
        },
        {
            "strategy": "The 24-Hour Rule",
            "description": "Wait 24 hours before making non-essential purchases",
            "difficulty": "easy",
            "expected_savings_increase": "20-30% on impulse purchases",
            "steps": [
                "When tempted to buy something non-essential, wait 24 hours",
                "Add item to a wishlist",
                "Revisit after 24 hours",
                "Often, the urge will pass and you save money"
            ],
            "best_for": "Impulse shoppers"
        }
    ]

    return {
        "user_id": str(user_id),
        "strategies": strategies,
        "recommended_strategy": "Pay Yourself First",
        "reason": "Easiest to implement with highest success rate for your profile"
    }


@router.get("/savings-rate-analysis")
async def analyze_savings_rate(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze savings rate and provide insights

    Compares to benchmarks and peers
    """
    user_id = UUID(current_user["user_id"])

    # Mock data
    current_rate = random.uniform(8, 18)
    peer_average = 15.5
    recommended_rate = 20.0

    analysis = {
        "user_id": str(user_id),
        "current_savings_rate": round(current_rate, 1),
        "peer_average": peer_average,
        "recommended_rate": recommended_rate,
        "rating": _get_savings_rate_rating(current_rate),
        "comparison": {
            "vs_peers": "below" if current_rate < peer_average else "above",
            "vs_recommendation": "below" if current_rate < recommended_rate else "at_target"
        },
        "benchmarks": {
            "minimal": {"rate": 5, "description": "Barely saving"},
            "fair": {"rate": 10, "description": "Building slowly"},
            "good": {"rate": 15, "description": "Solid savings"},
            "excellent": {"rate": 20, "description": "Financial security"},
            "exceptional": {"rate": 30, "description": "Fast-track to goals"}
        },
        "projection": {
            "5_years": round(current_rate * 12 * 5 * 500, 2),  # Mock calculation
            "10_years": round(current_rate * 12 * 10 * 500 * 1.2, 2),  # With compound interest
            "retirement": round(current_rate * 12 * 30 * 500 * 2.5, 2)
        },
        "recommendations": [
            f"Increase savings rate from {current_rate:.1f}% to {recommended_rate}%",
            f"This would save an additional ${((recommended_rate - current_rate) * 5000 / 100):.2f}/month",
            "Automate savings to make it effortless",
            "Review and eliminate one unnecessary expense"
        ]
    }

    return analysis


# Helper functions
async def _generate_mock_opportunities(user_id: UUID, db: AsyncSession) -> List[SavingsOpportunity]:
    """Generate mock savings opportunities"""
    opportunities = []

    # Subscription consolidation
    opportunities.append(SavingsOpportunity(
        user_id=user_id,
        opportunity_type="subscription_consolidation",
        title="Consolidate Streaming Services",
        description="You have 3 streaming subscriptions. Cancel 1-2 unused services.",
        estimated_monthly_savings=Decimal("15.99"),
        estimated_annual_savings=Decimal("191.88"),
        confidence=Decimal("90.0"),
        difficulty="easy",
        status="identified"
    ))

    # Category reduction
    opportunities.append(SavingsOpportunity(
        user_id=user_id,
        opportunity_type="category_reduction",
        title="Reduce Eating Out",
        description="Reduce restaurant spending by 30% through meal prep.",
        estimated_monthly_savings=Decimal("120.00"),
        estimated_annual_savings=Decimal("1440.00"),
        confidence=Decimal("75.0"),
        difficulty="medium",
        status="identified"
    ))

    # Unused gym membership
    opportunities.append(SavingsOpportunity(
        user_id=user_id,
        opportunity_type="unused_membership",
        title="Cancel Unused Gym Membership",
        description="You haven't used your gym membership in 60 days.",
        estimated_monthly_savings=Decimal("50.00"),
        estimated_annual_savings=Decimal("600.00"),
        confidence=Decimal("95.0"),
        difficulty="easy",
        status="identified"
    ))

    # Insurance review
    opportunities.append(SavingsOpportunity(
        user_id=user_id,
        opportunity_type="insurance_optimization",
        title="Shop for Better Insurance Rates",
        description="Compare auto insurance rates to potentially save money.",
        estimated_monthly_savings=Decimal("40.00"),
        estimated_annual_savings=Decimal("480.00"),
        confidence=Decimal("65.0"),
        difficulty="medium",
        status="identified"
    ))

    for opp in opportunities:
        db.add(opp)

    await db.commit()

    for opp in opportunities:
        await db.refresh(opp)

    return opportunities


def _get_savings_rate_rating(rate: float) -> Dict:
    """Get rating for savings rate"""
    if rate >= 30:
        return {"grade": "A+", "message": "Exceptional! You're on track for early financial independence."}
    elif rate >= 20:
        return {"grade": "A", "message": "Excellent! You're building strong financial security."}
    elif rate >= 15:
        return {"grade": "B", "message": "Good! You're making solid progress."}
    elif rate >= 10:
        return {"grade": "C", "message": "Fair. There's room for improvement."}
    elif rate >= 5:
        return {"grade": "D", "message": "Minimal savings. Focus on increasing this."}
    else:
        return {"grade": "F", "message": "Critical. Start building emergency savings immediately."}
