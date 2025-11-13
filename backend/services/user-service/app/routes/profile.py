"""
User profile routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException

from app.schemas import ProfileResponse, SubscriptionInfo
from app.models import User

router = APIRouter()


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    return user


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user subscription information and available features
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    # Define features by tier
    tier_features = {
        "free": [
            "Core budgeting and tracking",
            "Basic AI chat",
            "Spending insights",
            "Bill reminders",
            "Transaction categorization",
            "Standard autosave"
        ],
        "plus": [
            "All Free features",
            "Cash advances up to $250",
            "Enhanced financial insights",
            "Advanced autosave strategies",
            "Priority customer support"
        ],
        "builder": [
            "All Plus features",
            "Credit Builder secured card",
            "Credit score monitoring",
            "Credit coaching",
            "Cashback rewards (1%)",
            "Higher cash advance limits"
        ]
    }

    return SubscriptionInfo(
        subscription_tier=user.subscription_tier,
        features=tier_features.get(user.subscription_tier, tier_features["free"])
    )
