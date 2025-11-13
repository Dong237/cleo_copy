"""
Database models for Budget Service
"""
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from shared.database import Base
from shared.models import TimestampMixin


class Budget(Base, TimestampMixin):
    """Budget model"""

    __tablename__ = "budgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Budget details
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    period = Column(String(50), nullable=False, default="monthly")

    # Budget period
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)

    # Status
    is_active = Column(Boolean, nullable=False, default=True)

    # Alerts
    alert_at_75_percent = Column(Boolean, default=True)
    alert_at_90_percent = Column(Boolean, default=True)
    alert_at_100_percent = Column(Boolean, default=True)

    # Rollover settings
    allow_rollover = Column(Boolean, default=False)
    rollover_amount = Column(Numeric(12, 2), default=0)

    def __repr__(self):
        return f"<Budget(id={self.id}, name={self.name}, amount={self.amount})>"


class BudgetAlert(Base):
    """Budget Alert model"""

    __tablename__ = "budget_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    budget_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Alert details
    alert_type = Column(String(50), nullable=False)
    amount_spent = Column(Numeric(12, 2), nullable=False)
    budget_amount = Column(Numeric(12, 2), nullable=False)
    percentage_used = Column(Numeric(5, 2), nullable=False)

    # Status
    sent_at = Column(TimestampMixin.created_at.type, nullable=False)
    read_at = Column(TimestampMixin.created_at.type)

    created_at = Column(TimestampMixin.created_at.type, nullable=False)

    def __repr__(self):
        return f"<BudgetAlert(id={self.id}, type={self.alert_type})>"
