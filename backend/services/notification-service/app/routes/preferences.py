"""
Notification preferences routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user

from app.schemas import NotificationPreferencesUpdate, NotificationPreferencesResponse
from app.models import NotificationPreference

router = APIRouter()


@router.get("", response_model=NotificationPreferencesResponse)
async def get_preferences(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification preferences
    """
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user["user_id"]
        )
    )
    preferences = result.scalar_one_or_none()

    # Create default preferences if none exist
    if not preferences:
        preferences = NotificationPreference(
            user_id=current_user["user_id"]
        )
        db.add(preferences)
        await db.commit()
        await db.refresh(preferences)

    return preferences


@router.put("", response_model=NotificationPreferencesResponse)
async def update_preferences(
    preferences_update: NotificationPreferencesUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update notification preferences
    """
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user["user_id"]
        )
    )
    preferences = result.scalar_one_or_none()

    # Create if doesn't exist
    if not preferences:
        preferences = NotificationPreference(
            user_id=current_user["user_id"]
        )
        db.add(preferences)

    # Update fields
    update_data = preferences_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    await db.commit()
    await db.refresh(preferences)

    return preferences
