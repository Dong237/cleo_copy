"""
Database models for Advance Service
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from database import Base


class Advance(Base):
    """Cash advance records"""
    __tablename__ = "advances"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Advance details
    amount = Column(Numeric(12, 2), nullable=False)  # $20-$250
    status = Column(String(50), nullable=False, default="pending")  # pending, approved, disbursed, repaid, failed

    # Dates
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    approved_at = Column(DateTime)
    disbursed_at = Column(DateTime)
    repayment_due_date = Column(DateTime, nullable=False)
    repaid_at = Column(DateTime)

    # Fees
    instant_delivery_fee = Column(Numeric(12, 2), default=Decimal("0.00"))  # Optional $3-5
    tip_amount = Column(Numeric(12, 2), default=Decimal("0.00"))  # Optional tip
    total_amount = Column(Numeric(12, 2), nullable=False)  # amount + fees + tip

    # Underwriting
    risk_score = Column(Numeric(5, 2))  # 0-100
    underwriting_notes = Column(Text)

    # Repayment
    repayment_status = Column(String(50), default="pending")  # pending, scheduled, completed, failed
    repayment_attempts = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EligibilityCheck(Base):
    """Eligibility check history"""
    __tablename__ = "eligibility_checks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Eligibility results
    is_eligible = Column(Boolean, nullable=False)
    max_advance_amount = Column(Numeric(12, 2), nullable=False)  # $0-$250
    reason = Column(Text)

    # Factors considered
    has_regular_income = Column(Boolean)
    income_history_days = Column(Integer)
    has_recent_overdrafts = Column(Boolean)
    average_balance = Column(Numeric(12, 2))
    previous_advance_count = Column(Integer)
    previous_repayment_success_rate = Column(Numeric(5, 2))  # 0-100

    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Repayment(Base):
    """Repayment transaction records"""
    __tablename__ = "repayments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    advance_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Repayment details
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), nullable=False)  # scheduled, processing, completed, failed

    # Dates
    scheduled_date = Column(DateTime, nullable=False)
    attempted_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Payment method
    payment_method = Column(String(100))  # bank_debit, manual, etc.
    transaction_id = Column(String(255))  # External transaction ID

    # Failure handling
    failure_reason = Column(Text)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
