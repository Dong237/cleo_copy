"""
Spending recommendation routes
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import Recommendation, SpendingPattern
from app.schemas import (
    SpendingRecommendation,
    SpendingPatternResponse,
    Recommendation Response
)


router = APIRouter()


@router.get("/recommendations")
async def get_spending_recommendations(
    category: str = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized spending recommendations

    Analyzes spending patterns and suggests optimizations
    """
    user_id = UUID(current_user["user_id"])

    # In production, analyze real spending data
    # For now, generate smart mock recommendations

    recommendations = []

    categories_to_analyze = ["food", "transportation", "shopping", "entertainment"] if not category else [category]

    for cat in categories_to_analyze:
        current_spending = Decimal(str(random.randint(400, 800)))
        reduction_percentage = random.uniform(0.10, 0.25)  # 10-25% reduction
        recommended_spending = current_spending * Decimal(str(1 - reduction_percentage))
        potential_savings = current_spending - recommended_spending

        # Generate category-specific tips
        tips = _get_category_specific_tips(cat)

        recommendations.append(SpendingRecommendation(
            category=cat.title(),
            title=f"Reduce {cat.title()} Spending",
            description=f"You're spending ${current_spending}/month on {cat}. Based on similar users, you could save ${potential_savings:.2f}/month.",
            current_monthly_spending=current_spending,
            recommended_monthly_spending=recommended_spending,
            potential_savings=potential_savings,
            difficulty="medium" if reduction_percentage < 0.20 else "easy",
            tips=tips[:3]
        ))

    # Sort by potential savings
    recommendations.sort(key=lambda x: x.potential_savings, reverse=True)

    return {
        "user_id": str(user_id),
        "recommendations": recommendations,
        "total_potential_savings": sum(r.potential_savings for r in recommendations)
    }


@router.get("/patterns", response_model=List[SpendingPatternResponse])
async def get_spending_patterns(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Identify spending patterns using ML

    Detects:
    - Recurring expenses
    - Spending spikes
    - Trends (increasing/decreasing)
    """
    user_id = UUID(current_user["user_id"])

    # Get existing patterns or generate mock
    result = await db.execute(
        select(SpendingPattern)
        .where(SpendingPattern.user_id == user_id)
        .order_by(SpendingPattern.confidence.desc())
    )

    patterns = result.scalars().all()

    if not patterns:
        # Generate mock patterns
        patterns = await _generate_mock_patterns(user_id, db)

    return [
        SpendingPatternResponse(
            id=pattern.id,
            pattern_type=pattern.pattern_type,
            category=pattern.category,
            description=pattern.description,
            frequency=pattern.frequency,
            average_amount=pattern.average_amount,
            trend=pattern.trend,
            confidence=pattern.confidence,
            first_detected=pattern.first_detected
        )
        for pattern in patterns
    ]


@router.get("/alerts")
async def get_spending_alerts(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get spending alerts and warnings

    Alerts for:
    - Unusual spending
    - Budget overruns
    - Expensive subscriptions
    """
    user_id = UUID(current_user["user_id"])

    alerts = []

    # Mock unusual spending alert
    if random.random() > 0.5:
        alerts.append({
            "alert_type": "unusual_spending",
            "severity": "warning",
            "title": "Unusual Spending Detected",
            "message": "You spent $245 on shopping yesterday, 3x your usual daily average.",
            "category": "shopping",
            "amount": 245.00,
            "recommendation": "Review recent purchases and ensure they align with your budget."
        })

    # Mock budget overage alert
    if random.random() > 0.4:
        alerts.append({
            "alert_type": "budget_overage",
            "severity": "critical",
            "title": "Budget Exceeded",
            "message": "You've exceeded your Food & Dining budget by $87 this month.",
            "category": "food",
            "amount": 87.00,
            "recommendation": "Consider reducing eating out for the rest of the month."
        })

    # Mock subscription alert
    if random.random() > 0.6:
        alerts.append({
            "alert_type": "expensive_subscription",
            "severity": "info",
            "title": "Subscription Review",
            "message": "You have 3 streaming subscriptions costing $45/month. Are you using all of them?",
            "category": "entertainment",
            "amount": 45.00,
            "recommendation": "Cancel unused subscriptions to save $15-30/month."
        })

    return {
        "user_id": str(user_id),
        "alerts": alerts,
        "total_alerts": len(alerts),
        "critical_count": sum(1 for a in alerts if a["severity"] == "critical")
    }


@router.post("/optimize-category")
async def optimize_category_spending(
    category: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get deep optimization recommendations for specific category

    Provides detailed analysis and actionable steps
    """
    user_id = UUID(current_user["user_id"])

    # Mock deep analysis
    current_spending = Decimal(str(random.randint(400, 800)))
    peer_average = current_spending * Decimal(str(random.uniform(0.7, 0.9)))

    analysis = {
        "category": category.title(),
        "current_monthly_spending": float(current_spending),
        "peer_average": float(peer_average),
        "percentile": random.randint(60, 95),  # User is spending more than X% of peers
        "breakdown": {
            "fixed_costs": float(current_spending * Decimal("0.4")),
            "variable_costs": float(current_spending * Decimal("0.6"))
        },
        "optimization_opportunities": [
            {
                "opportunity": "Switch to cheaper alternatives",
                "potential_savings": float(current_spending * Decimal("0.15")),
                "difficulty": "easy",
                "specific_actions": _get_category_optimization_actions(category)
            },
            {
                "opportunity": "Reduce frequency",
                "potential_savings": float(current_spending * Decimal("0.20")),
                "difficulty": "medium",
                "specific_actions": [
                    f"Cut {category} spending by 20%",
                    "Plan purchases in advance",
                    "Set weekly spending limits"
                ]
            }
        ],
        "recommended_monthly_budget": float(peer_average),
        "expected_annual_savings": float((current_spending - peer_average) * 12)
    }

    return analysis


# Helper functions
def _get_category_specific_tips(category: str) -> List[str]:
    """Get category-specific money-saving tips"""
    tips_by_category = {
        "food": [
            "Meal prep on Sundays to reduce eating out",
            "Use grocery store loyalty programs and coupons",
            "Buy generic brands for staples",
            "Cook larger batches and freeze portions",
            "Shop with a list to avoid impulse purchases"
        ],
        "transportation": [
            "Use public transit when possible",
            "Carpool with coworkers",
            "Combine errands into single trips",
            "Keep tires properly inflated for better gas mileage",
            "Compare gas prices with apps like GasBuddy"
        ],
        "shopping": [
            "Wait 24 hours before making non-essential purchases",
            "Use cashback apps and browser extensions",
            "Buy secondhand when possible",
            "Unsubscribe from promotional emails",
            "Set a monthly shopping budget and stick to it"
        ],
        "entertainment": [
            "Share streaming subscriptions with family",
            "Look for free local events and activities",
            "Use library resources (books, movies, museum passes)",
            "Host game nights instead of going out",
            "Take advantage of happy hour specials"
        ]
    }

    return tips_by_category.get(category, [
        "Track your spending in this category",
        "Set a budget and monitor it weekly",
        "Look for cheaper alternatives"
    ])


def _get_category_optimization_actions(category: str) -> List[str]:
    """Get specific optimization actions for category"""
    actions = {
        "food": [
            "Switch from brand name to store brands",
            "Buy in bulk at warehouse stores",
            "Use meal planning apps"
        ],
        "transportation": [
            "Switch to a more fuel-efficient vehicle",
            "Use apps like Waze to find cheapest gas",
            "Consider biking for short trips"
        ],
        "shopping": [
            "Use price comparison tools",
            "Wait for sales and use coupons",
            "Buy quality items that last longer"
        ],
        "entertainment": [
            "Cancel unused subscriptions",
            "Use free trials strategically",
            "Look for student/military discounts"
        ]
    }

    return actions.get(category, ["Review spending in this category", "Set limits"])


async def _generate_mock_patterns(user_id: UUID, db: AsyncSession) -> List[SpendingPattern]:
    """Generate mock spending patterns"""
    patterns = []

    # Recurring subscription pattern
    patterns.append(SpendingPattern(
        user_id=user_id,
        pattern_type="recurring",
        category="Entertainment",
        description="Monthly streaming subscriptions detected",
        frequency="monthly",
        average_amount=Decimal("45.99"),
        trend="stable",
        confidence=Decimal("95.0"),
        first_detected=datetime.utcnow() - timedelta(days=90)
    ))

    # Spending spike pattern
    patterns.append(SpendingPattern(
        user_id=user_id,
        pattern_type="spike",
        category="Shopping",
        description="Weekend spending spikes detected",
        frequency="weekly",
        average_amount=Decimal("180.00"),
        trend="increasing",
        confidence=Decimal("82.5"),
        first_detected=datetime.utcnow() - timedelta(days=60)
    ))

    # Trend pattern
    patterns.append(SpendingPattern(
        user_id=user_id,
        pattern_type="trend",
        category="Food & Dining",
        description="Gradual increase in eating out",
        frequency="daily",
        average_amount=Decimal("25.00"),
        trend="increasing",
        confidence=Decimal("78.0"),
        first_detected=datetime.utcnow() - timedelta(days=45)
    ))

    for pattern in patterns:
        db.add(pattern)

    await db.commit()

    for pattern in patterns:
        await db.refresh(pattern)

    return patterns
