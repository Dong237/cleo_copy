"""
Database models for User Service
"""
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from shared.database import Base
from shared.models import TimestampMixin


class PersonalityMode(str, enum.Enum):
    """AI personality modes"""
    FUNNY = "funny"
    SUPPORTIVE = "supportive"
    STRICT = "strict"
    ROAST = "roast"


class User(Base, TimestampMixin):
    """User model"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    profile_photo_url = Column(String(500), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)

    # Preferences
    personality_mode = Column(
        SQLEnum(PersonalityMode),
        default=PersonalityMode.SUPPORTIVE,
        nullable=False
    )
    notification_enabled = Column(Boolean, default=True, nullable=False)

    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)

    # Subscription tier
    subscription_tier = Column(
        String(50),
        default="free",
        nullable=False
    )  # free, plus, builder

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
