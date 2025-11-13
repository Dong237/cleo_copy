"""
Database models for Notification Service
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from shared.database import Base
from shared.models import TimestampMixin


class Notification(Base, TimestampMixin):
    """Notification model"""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Notification details
    type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)

    # Delivery
    channel = Column(String(50), nullable=False)  # push, sms, email, in_app
    priority = Column(String(50), default="medium")  # low, medium, high, urgent

    # Status
    status = Column(String(50), nullable=False, default="pending")  # pending, sent, failed, cancelled
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))

    # Metadata
    data = Column(JSONB)  # Additional data for deep linking, etc.

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type})>"


class NotificationPreference(Base, TimestampMixin):
    """Notification Preferences model"""

    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)

    # Channel preferences
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    email_enabled = Column(Boolean, default=True)

    # Category preferences
    budget_alerts_enabled = Column(Boolean, default=True)
    bill_reminders_enabled = Column(Boolean, default=True)
    insights_enabled = Column(Boolean, default=True)
    achievements_enabled = Column(Boolean, default=True)
    marketing_enabled = Column(Boolean, default=False)

    # Quiet hours
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))

    # Frequency
    digest_frequency = Column(String(50), default="daily")  # real_time, daily, weekly, never

    def __repr__(self):
        return f"<NotificationPreference(user_id={self.user_id})>"
