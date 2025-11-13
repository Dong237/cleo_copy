"""
Database models for Chat Service
"""
from sqlalchemy import Column, String, ForeignKey, Text, Integer, Boolean, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from shared.database import Base
from shared.models import TimestampMixin


class Conversation(Base, TimestampMixin):
    """Conversation model"""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Conversation metadata
    title = Column(String(255))
    personality_mode = Column(String(50))

    # Status
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"


class Message(Base):
    """Message model"""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Message content
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # AI metadata
    intent = Column(String(100), index=True)  # Detected intent
    confidence = Column(Numeric(5, 4))
    response_time_ms = Column(Integer)

    # User feedback
    helpful = Column(Boolean)
    feedback_text = Column(Text)

    # Timestamps
    created_at = Column(TimestampMixin.created_at.type, nullable=False)

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"
