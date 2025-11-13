"""
Database models for Credit Service
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, Integer, Date
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from database import Base


class CreditScore(Base):
    """Credit score history and monitoring"""
    __tablename__ = "credit_scores"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Credit score data
    score = Column(Integer, nullable=False)  # 300-850
    score_provider = Column(String(100), default="TransUnion")  # TransUnion, Equifax, Experian
    score_model = Column(String(100), default="VantageScore 3.0")

    # Score factors
    factors = Column(JSONB)  # Factors affecting score
    credit_utilization = Column(Numeric(5, 2))  # Percentage
    payment_history_score = Column(Integer)  # 0-100
    credit_age_months = Column(Integer)
    total_accounts = Column(Integer)
    hard_inquiries = Column(Integer)

    # Change tracking
    previous_score = Column(Integer)
    score_change = Column(Integer)  # Positive or negative change

    # Monitoring
    alert_threshold = Column(Integer, default=10)  # Alert if change > threshold
    monitoring_enabled = Column(Boolean, default=True)

    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class CreditBuilderCard(Base):
    """Credit builder card accounts"""
    __tablename__ = "credit_builder_cards"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True, unique=True)

    # Card details
    card_number_last4 = Column(String(4))
    status = Column(String(50), nullable=False, default="pending")  # pending, active, closed, suspended
    credit_limit = Column(Numeric(12, 2), default=Decimal("500.00"))
    available_credit = Column(Numeric(12, 2), default=Decimal("500.00"))
    current_balance = Column(Numeric(12, 2), default=Decimal("0.00"))

    # Security deposit (for secured card)
    security_deposit = Column(Numeric(12, 2))
    deposit_status = Column(String(50))  # pending, held, returned

    # Dates
    applied_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    activated_at = Column(DateTime)
    closed_at = Column(DateTime)

    # Settings
    autopay_enabled = Column(Boolean, default=True)
    statement_day = Column(Integer, default=1)  # Day of month
    due_day = Column(Integer, default=15)  # Day of month

    # Performance tracking
    on_time_payments = Column(Integer, default=0)
    late_payments = Column(Integer, default=0)
    months_active = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreditBuilderTransaction(Base):
    """Transactions on credit builder card"""
    __tablename__ = "credit_builder_transactions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    card_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Transaction details
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # purchase, payment, fee, interest
    merchant_name = Column(String(255))
    category = Column(String(100))

    # Status
    status = Column(String(50), default="posted")  # pending, posted, reversed

    # Dates
    transaction_date = Column(Date, nullable=False)
    posted_date = Column(Date)

    # Reference
    description = Column(Text)
    external_transaction_id = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)


class CreditBuilderPayment(Base):
    """Payment history for credit builder card"""
    __tablename__ = "credit_builder_payments"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    card_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Payment details
    amount = Column(Numeric(12, 2), nullable=False)
    payment_type = Column(String(50))  # minimum, full, custom
    payment_method = Column(String(100))  # bank_debit, manual

    # Status
    status = Column(String(50), nullable=False)  # scheduled, processing, completed, failed
    is_autopay = Column(Boolean, default=False)

    # Dates
    due_date = Column(Date, nullable=False)
    scheduled_date = Column(Date)
    completed_date = Column(Date)

    # On-time tracking
    is_on_time = Column(Boolean)
    days_late = Column(Integer, default=0)

    # Failure handling
    failure_reason = Column(Text)
    retry_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreditCoachingSession(Base):
    """Credit coaching and education sessions"""
    __tablename__ = "credit_coaching_sessions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Session details
    topic = Column(String(255), nullable=False)  # credit_utilization, payment_history, etc.
    content = Column(Text)
    recommendations = Column(JSONB)

    # Progress tracking
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    # Impact
    estimated_score_impact = Column(Integer)  # Estimated points improvement

    created_at = Column(DateTime, default=datetime.utcnow)


class CreditAlert(Base):
    """Credit monitoring alerts"""
    __tablename__ = "credit_alerts"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Alert details
    alert_type = Column(String(100), nullable=False)  # score_change, new_account, hard_inquiry, etc.
    severity = Column(String(50), default="info")  # info, warning, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Alert data
    alert_data = Column(JSONB)  # Additional structured data

    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    is_dismissed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
