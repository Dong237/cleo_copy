"""
Database models for Analytics Service
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Numeric, DateTime, Integer, Text, Date
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from database import Base


class UserAnalytics(Base):
    """User behavior and engagement analytics"""
    __tablename__ = "user_analytics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Engagement metrics
    session_count = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    average_session_duration_seconds = Column(Integer, default=0)
    last_active_at = Column(DateTime)

    # Feature usage
    chat_messages_sent = Column(Integer, default=0)
    budgets_created = Column(Integer, default=0)
    savings_goals_created = Column(Integer, default=0)
    advances_requested = Column(Integer, default=0)

    # Financial health indicators
    total_saved = Column(Numeric(12, 2), default=Decimal("0.00"))
    total_advanced = Column(Numeric(12, 2), default=Decimal("0.00"))
    credit_score_improvement = Column(Integer, default=0)

    # Time period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FinancialMetrics(Base):
    """Aggregated financial metrics"""
    __tablename__ = "financial_metrics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Income metrics
    total_income = Column(Numeric(12, 2), default=Decimal("0.00"))
    average_monthly_income = Column(Numeric(12, 2), default=Decimal("0.00"))

    # Spending metrics
    total_spending = Column(Numeric(12, 2), default=Decimal("0.00"))
    average_monthly_spending = Column(Numeric(12, 2), default=Decimal("0.00"))

    # Category breakdown (JSONB for flexibility)
    spending_by_category = Column(JSONB)  # {"food": 500, "transport": 200, ...}

    # Savings metrics
    total_saved = Column(Numeric(12, 2), default=Decimal("0.00"))
    savings_rate = Column(Numeric(5, 2))  # Percentage

    # Budget adherence
    budget_adherence_rate = Column(Numeric(5, 2))  # Percentage
    over_budget_categories = Column(JSONB)

    # Time period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class BusinessMetrics(Base):
    """Business-level aggregated metrics"""
    __tablename__ = "business_metrics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # User metrics
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    churned_users = Column(Integer, default=0)

    # Subscription metrics
    free_tier_users = Column(Integer, default=0)
    plus_tier_users = Column(Integer, default=0)
    builder_tier_users = Column(Integer, default=0)

    # Revenue metrics (mock for development)
    mrr = Column(Numeric(12, 2), default=Decimal("0.00"))  # Monthly Recurring Revenue
    arr = Column(Numeric(12, 2), default=Decimal("0.00"))  # Annual Recurring Revenue

    # Engagement metrics
    average_sessions_per_user = Column(Numeric(5, 2))
    average_session_duration = Column(Integer)  # seconds

    # Financial product usage
    total_advances_issued = Column(Integer, default=0)
    total_advance_amount = Column(Numeric(12, 2), default=Decimal("0.00"))
    credit_builder_cards_active = Column(Integer, default=0)

    # Time period
    period_date = Column(Date, nullable=False, unique=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class EventLog(Base):
    """Event tracking for user actions"""
    __tablename__ = "event_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), index=True)

    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(100), nullable=False)
    event_name = Column(String(255), nullable=False)

    # Event data
    event_data = Column(JSONB)

    # Context
    service_name = Column(String(100))
    session_id = Column(String(255))

    # Timestamp
    event_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
