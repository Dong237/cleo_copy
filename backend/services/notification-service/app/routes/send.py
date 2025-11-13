"""
Send notification routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user

from app.schemas import (
    SendPushNotification,
    SendSMSNotification,
    SendEmailNotification,
    SendNotificationResponse,
    BatchNotificationCreate,
    BatchNotificationResponse
)
from app.models import Notification
from app.providers.push_provider import send_push_notification
from app.providers.sms_provider import send_sms
from app.providers.email_provider import send_email

router = APIRouter()


@router.post("/push", response_model=SendNotificationResponse)
async def send_push(
    notification_data: SendPushNotification,
    db: AsyncSession = Depends(get_db)
):
    """
    Send push notification
    """
    # Create notification record
    notification = Notification(
        user_id=notification_data.user_id,
        type="push_notification",
        title=notification_data.title,
        body=notification_data.body,
        channel="push",
        priority="medium",
        data=notification_data.data,
        status="pending"
    )

    db.add(notification)
    await db.flush()

    # Send via Firebase Cloud Messaging
    try:
        success = await send_push_notification(
            notification_data.user_id,
            notification_data.title,
            notification_data.body,
            notification_data.data
        )

        if success:
            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
            message = "Push notification sent successfully"
        else:
            notification.status = "failed"
            message = "Failed to send push notification"

    except Exception as e:
        notification.status = "failed"
        message = f"Error sending push notification: {str(e)}"

    await db.commit()

    return SendNotificationResponse(
        notification_id=notification.id,
        status=notification.status,
        message=message
    )


@router.post("/sms", response_model=SendNotificationResponse)
async def send_sms_notification(
    notification_data: SendSMSNotification,
    db: AsyncSession = Depends(get_db)
):
    """
    Send SMS notification via Twilio
    """
    # Create notification record
    notification = Notification(
        user_id=notification_data.user_id,
        type="sms_notification",
        title="SMS",
        body=notification_data.message,
        channel="sms",
        priority="high",
        status="pending"
    )

    db.add(notification)
    await db.flush()

    # Send via Twilio
    try:
        success = await send_sms(
            notification_data.user_id,
            notification_data.message
        )

        if success:
            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
            message = "SMS sent successfully"
        else:
            notification.status = "failed"
            message = "Failed to send SMS"

    except Exception as e:
        notification.status = "failed"
        message = f"Error sending SMS: {str(e)}"

    await db.commit()

    return SendNotificationResponse(
        notification_id=notification.id,
        status=notification.status,
        message=message
    )


@router.post("/email", response_model=SendNotificationResponse)
async def send_email_notification(
    notification_data: SendEmailNotification,
    db: AsyncSession = Depends(get_db)
):
    """
    Send email notification via SendGrid
    """
    # Create notification record
    notification = Notification(
        user_id=notification_data.user_id,
        type="email_notification",
        title=notification_data.subject,
        body=notification_data.body,
        channel="email",
        priority="low",
        status="pending"
    )

    db.add(notification)
    await db.flush()

    # Send via SendGrid
    try:
        success = await send_email(
            notification_data.user_id,
            notification_data.subject,
            notification_data.body,
            notification_data.html
        )

        if success:
            notification.status = "sent"
            notification.sent_at = datetime.utcnow()
            message = "Email sent successfully"
        else:
            notification.status = "failed"
            message = "Failed to send email"

    except Exception as e:
        notification.status = "failed"
        message = f"Error sending email: {str(e)}"

    await db.commit()

    return SendNotificationResponse(
        notification_id=notification.id,
        status=notification.status,
        message=message
    )


@router.post("/batch", response_model=BatchNotificationResponse)
async def send_batch_notifications(
    batch_data: BatchNotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Send notifications to multiple users
    """
    notification_ids = []
    sent_count = 0
    failed_count = 0

    for user_id in batch_data.user_ids:
        notification = Notification(
            user_id=user_id,
            type=batch_data.type,
            title=batch_data.title,
            body=batch_data.body,
            channel=batch_data.channel,
            priority=batch_data.priority,
            data=batch_data.data,
            status="pending"
        )

        db.add(notification)
        await db.flush()

        # Send based on channel
        try:
            if batch_data.channel == "push":
                success = await send_push_notification(user_id, batch_data.title, batch_data.body, batch_data.data)
            elif batch_data.channel == "sms":
                success = await send_sms(user_id, batch_data.body)
            elif batch_data.channel == "email":
                success = await send_email(user_id, batch_data.title, batch_data.body)
            else:
                success = True  # in_app notifications don't need external sending

            if success:
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
                sent_count += 1
            else:
                notification.status = "failed"
                failed_count += 1

        except Exception:
            notification.status = "failed"
            failed_count += 1

        notification_ids.append(notification.id)

    await db.commit()

    return BatchNotificationResponse(
        total_sent=sent_count,
        total_failed=failed_count,
        notification_ids=notification_ids
    )
