"""
User management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user, get_password_hash, verify_password
from shared.exceptions import NotFoundException, AuthenticationException, ValidationException

from app.schemas import (
    UserResponse,
    UserUpdate,
    PasswordChange,
    PersonalityModeUpdate,
    NotificationSettings
)
from app.models import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user information
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    # Update fields if provided
    if user_update.first_name is not None:
        user.first_name = user_update.first_name
    if user_update.last_name is not None:
        user.last_name = user_update.last_name
    if user_update.phone_number is not None:
        user.phone_number = user_update.phone_number
    if user_update.profile_photo_url is not None:
        user.profile_photo_url = user_update.profile_photo_url

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/me/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    # Verify current password
    if not verify_password(password_change.current_password, user.hashed_password):
        raise AuthenticationException("Current password is incorrect")

    # Update password
    user.hashed_password = get_password_hash(password_change.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.put("/me/personality", response_model=UserResponse)
async def update_personality_mode(
    personality_update: PersonalityModeUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update AI personality mode
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    user.personality_mode = personality_update.personality_mode
    await db.commit()
    await db.refresh(user)

    return user


@router.put("/me/notifications")
async def update_notification_settings(
    notification_settings: NotificationSettings,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update notification settings
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    user.notification_enabled = notification_settings.notification_enabled
    await db.commit()

    return {"message": "Notification settings updated"}


@router.delete("/me")
async def delete_account(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account (soft delete - deactivate)
    """
    result = await db.execute(select(User).where(User.id == current_user["user_id"]))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException("User not found")

    # Soft delete - deactivate account
    user.is_active = False
    await db.commit()

    return {"message": "Account deactivated successfully"}
