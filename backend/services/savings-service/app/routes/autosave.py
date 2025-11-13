"""
Autosave management and recommendations routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from decimal import Decimal
import random

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user

from app.schemas import (
    AutosaveSettingsUpdate,
    AutosaveSettingsResponse,
    AutosaveRecommendation
)

router = APIRouter()


@router.get("/settings", response_model=AutosaveSettingsResponse)
async def get_autosave_settings(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current autosave settings
    In production, this would fetch user's actual settings
    """
    # Mock settings for development
    return AutosaveSettingsResponse(
        enabled=True,
        amount=Decimal("50.00"),
        frequency="weekly",
        goal_id=None,  # Could be tied to specific goal
        next_autosave_date=date.today() + timedelta(days=7),
        estimated_monthly_savings=Decimal("200.00")
    )


@router.put("/settings", response_model=AutosaveSettingsResponse)
async def update_autosave_settings(
    settings: AutosaveSettingsUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update autosave settings
    """
    # In production, save settings to database or user preferences

    # Calculate next autosave date based on frequency
    next_date = date.today()
    if settings.frequency == "daily":
        next_date += timedelta(days=1)
    elif settings.frequency == "weekly":
        next_date += timedelta(days=7)
    elif settings.frequency == "bi-weekly":
        next_date += timedelta(days=14)
    elif settings.frequency == "monthly":
        next_date += timedelta(days=30)

    # Calculate estimated monthly savings
    if settings.amount:
        if settings.frequency == "daily":
            monthly = float(settings.amount) * 30
        elif settings.frequency == "weekly":
            monthly = float(settings.amount) * 4.33
        elif settings.frequency == "bi-weekly":
            monthly = float(settings.amount) * 2.17
        else:  # monthly
            monthly = float(settings.amount)
    else:
        monthly = 0

    return AutosaveSettingsResponse(
        enabled=settings.enabled,
        amount=settings.amount,
        frequency=settings.frequency,
        goal_id=settings.goal_id,
        next_autosave_date=next_date if settings.enabled else None,
        estimated_monthly_savings=Decimal(str(monthly))
    )


@router.get("/recommendation", response_model=AutosaveRecommendation)
async def get_autosave_recommendation(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-recommended autosave amount based on spending patterns
    In production, this would analyze:
    - Income patterns
    - Spending history
    - Upcoming bills
    - Current balance
    - Historical overdrafts
    """
    # Mock recommendation with simple logic
    # In production, this would use ML model

    # Simulate analysis
    monthly_income = Decimal("3000.00")
    monthly_expenses = Decimal("2400.00")
    upcoming_bills = Decimal("300.00")
    current_balance = Decimal("2750.00")

    # Calculate safe to save
    available = monthly_income - monthly_expenses - upcoming_bills
    safe_to_save = max(available * Decimal("0.5"), Decimal("0"))  # 50% of available

    # Recommend weekly autosave
    recommended_weekly = safe_to_save / Decimal("4.33")  # weeks in month

    # Round to nearest $5
    recommended_weekly = (recommended_weekly / 5).quantize(Decimal("1")) * 5

    reasoning_parts = []
    if available > 0:
        reasoning_parts.append(f"You have ${available:.2f} available after expenses")
        reasoning_parts.append(f"Recommended to save 50% of available income")
        reasoning_parts.append("This ensures you won't overdraft")
    else:
        reasoning_parts.append("Your expenses match your income")
        reasoning_parts.append("Focus on reducing expenses first")
        recommended_weekly = Decimal("0")

    return AutosaveRecommendation(
        recommended_amount=max(recommended_weekly, Decimal("10")),  # Minimum $10
        frequency="weekly",
        reasoning=". ".join(reasoning_parts),
        safe_to_save=safe_to_save,
        projected_monthly_savings=max(recommended_weekly, Decimal("10")) * Decimal("4.33")
    )


@router.post("/execute")
async def execute_autosave(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger autosave (for testing)
    In production, this would be called by a scheduled job
    """
    # This would:
    # 1. Check user's autosave settings
    # 2. Verify sufficient balance
    # 3. Transfer money to savings
    # 4. Create savings transaction record
    # 5. Send notification

    return {
        "message": "Autosave executed successfully",
        "amount": "50.00",
        "goal": "Emergency Fund",
        "new_balance": "1250.00"
    }
