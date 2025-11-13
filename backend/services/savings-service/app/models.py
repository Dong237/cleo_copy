"""
Database models for Savings Service
"""
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import date

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from shared.database import Base
from shared.models import TimestampMixin


class SavingsGoal(Base, TimestampMixin):
    """Savings Goal model"""

    __tablename__ = "savings_goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Goal details
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    goal_type = Column(String(100))  # emergency_fund, vacation, car, home, wedding, custom

    # Financial details
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), nullable=False, default=0)
    currency = Column(String(3), default="USD")

    # Timeline
    target_date = Column(Date)
    started_at = Column(Date, nullable=False, default=date.today)
    completed_at = Column(Date)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    is_completed = Column(Boolean, nullable=False, default=False)

    # Autosave settings
    autosave_enabled = Column(Boolean, default=False)
    autosave_amount = Column(Numeric(12, 2))
    autosave_frequency = Column(String(50))  # daily, weekly, bi-weekly, monthly

    def __repr__(self):
        return f"<SavingsGoal(id={self.id}, name={self.name})>"


class SavingsTransaction(Base, TimestampMixin):
    """Savings Transaction model"""

    __tablename__ = "savings_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    goal_id = Column(UUID(as_uuid=True), index=True)  # Can be NULL for general savings

    # Transaction details
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # deposit, withdrawal
    method = Column(String(100))  # autosave, manual, round_up, spare_change

    # Status
    status = Column(String(50), nullable=False, default="pending")  # pending, completed, failed
    processed_at = Column(DateTime(timezone=True))

    # Metadata
    description = Column(String(500))

    def __repr__(self):
        return f"<SavingsTransaction(id={self.id}, amount={self.amount})>"
