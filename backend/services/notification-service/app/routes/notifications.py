"""
Notification management routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException

from app.schemas import NotificationListResponse, NotificationResponse
from app.models import Notification

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's notifications
    """
    query = select(Notification).where(
        Notification.user_id == current_user["user_id"]
    )

    if unread_only:
        query = query.where(Notification.read_at.is_(None))

    query = query.order_by(desc(Notification.created_at)).limit(limit)

    result = await db.execute(query)
    notifications = result.scalars().all()

    # Count unread
    unread_query = select(func.count()).select_from(Notification).where(
        and_(
            Notification.user_id == current_user["user_id"],
            Notification.read_at.is_(None)
        )
    )
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar()

    return NotificationListResponse(
        notifications=notifications,
        total=len(notifications),
        unread_count=unread_count
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific notification
    """
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user["user_id"]
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise NotFoundException("Notification not found")

    return notification


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark notification as read
    """
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user["user_id"]
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise NotFoundException("Notification not found")

    notification.read_at = datetime.utcnow()
    await db.commit()

    return {"message": "Notification marked as read"}


@router.post("/{notification_id}/clicked")
async def mark_as_clicked(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark notification as clicked
    """
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user["user_id"]
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise NotFoundException("Notification not found")

    notification.clicked_at = datetime.utcnow()
    if not notification.read_at:
        notification.read_at = datetime.utcnow()
    await db.commit()

    return {"message": "Notification marked as clicked"}


@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark all notifications as read
    """
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user["user_id"],
                Notification.read_at.is_(None)
            )
        )
    )
    notifications = result.scalars().all()

    for notification in notifications:
        notification.read_at = datetime.utcnow()

    await db.commit()

    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete notification
    """
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user["user_id"]
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise NotFoundException("Notification not found")

    await db.delete(notification)
    await db.commit()

    return {"message": "Notification deleted"}
