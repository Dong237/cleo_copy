"""
Database models for Recommendation Service
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from database import Base


class Recommendation(Base):
    """Personalized recommendations"""
    __tablename__ = "recommendations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Recommendation details
    recommendation_type = Column(String(100), nullable=False)  # spending, savings, budget, credit
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Priority and impact
    priority = Column(String(50), nullable=False)  # high, medium, low
    estimated_savings = Column(Numeric(12, 2))  # Potential savings
    confidence_score = Column(Numeric(5, 2))  # 0-100

    # Action items
    action_items = Column(JSONB)  # List of actionable steps

    # Status
    status = Column(String(50), default="active")  # active, dismissed, completed
    viewed = Column(Boolean, default=False)
    acted_on = Column(Boolean, default=False)

    # Metadata
    recommendation_data = Column(JSONB)  # Additional structured data
    model_version = Column(String(50))

    # Dates
    valid_until = Column(DateTime)
    viewed_at = Column(DateTime)
    acted_on_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SpendingPattern(Base):
    """Identified spending patterns"""
    __tablename__ = "spending_patterns"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Pattern details
    pattern_type = Column(String(100), nullable=False)  # recurring, spike, trend
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    # Pattern characteristics
    frequency = Column(String(50))  # daily, weekly, monthly
    average_amount = Column(Numeric(12, 2))
    trend = Column(String(50))  # increasing, decreasing, stable

    # Detection
    confidence = Column(Numeric(5, 2))  # 0-100
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_occurrence = Column(DateTime)

    # Pattern data
    pattern_data = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavingsOpportunity(Base):
    """Identified savings opportunities"""
    __tablename__ = "savings_opportunities"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)

    # Opportunity details
    opportunity_type = Column(String(100), nullable=False)  # subscription, category_reduction, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Savings potential
    estimated_monthly_savings = Column(Numeric(12, 2), nullable=False)
    estimated_annual_savings = Column(Numeric(12, 2), nullable=False)
    confidence = Column(Numeric(5, 2))  # 0-100

    # Difficulty
    difficulty = Column(String(50))  # easy, medium, hard

    # Status
    status = Column(String(50), default="identified")  # identified, presented, acted_on
    presented_at = Column(DateTime)
    acted_on_at = Column(DateTime)

    # Opportunity data
    opportunity_data = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow)


class InsightFeedback(Base):
    """User feedback on recommendations and insights"""
    __tablename__ = "insight_feedback"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    recommendation_id = Column(PGUUID(as_uuid=True), index=True)

    # Feedback
    helpful = Column(Boolean)
    rating = Column(Integer)  # 1-5
    feedback_text = Column(Text)

    # Action taken
    action_taken = Column(Boolean, default=False)
    action_description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
