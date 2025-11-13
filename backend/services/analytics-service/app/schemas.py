"""
Pydantic schemas for Analytics Service
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, List, Any
from uuid import UUID
from pydantic import BaseModel, Field


# User Analytics Schemas
class UserEngagementMetrics(BaseModel):
    """User engagement metrics"""
    user_id: UUID
    total_sessions: int
    average_session_duration_seconds: int
    last_active_at: Optional[datetime] = None
    chat_messages_sent: int
    budgets_created: int
    savings_goals_created: int
    advances_requested: int


class UserFinancialHealth(BaseModel):
    """User financial health indicators"""
    user_id: UUID
    total_saved: Decimal
    total_advanced: Decimal
    credit_score_improvement: int
    savings_rate: Optional[Decimal] = None
    budget_adherence_rate: Optional[Decimal] = None


class UserAnalyticsSummary(BaseModel):
    """Complete user analytics summary"""
    user_id: UUID
    engagement: UserEngagementMetrics
    financial_health: UserFinancialHealth
    period_start: date
    period_end: date


# Financial Analytics Schemas
class SpendingBreakdown(BaseModel):
    """Spending breakdown by category"""
    category: str
    amount: Decimal
    percentage: Decimal
    trend: str  # increasing, decreasing, stable


class FinancialAnalyticsSummary(BaseModel):
    """Financial analytics summary"""
    user_id: UUID
    total_income: Decimal
    total_spending: Decimal
    total_saved: Decimal
    savings_rate: Decimal
    average_monthly_income: Decimal
    average_monthly_spending: Decimal
    spending_by_category: List[SpendingBreakdown]
    budget_adherence_rate: Decimal
    over_budget_categories: List[str]
    period_start: date
    period_end: date


class IncomeVsSpendingTrend(BaseModel):
    """Income vs spending trend"""
    month: str
    income: Decimal
    spending: Decimal
    savings: Decimal
    savings_rate: Decimal


# Business Intelligence Schemas
class BusinessMetricsSummary(BaseModel):
    """Business metrics summary"""
    total_users: int
    new_users: int
    active_users: int
    churned_users: int

    free_tier_users: int
    plus_tier_users: int
    builder_tier_users: int

    mrr: Decimal
    arr: Decimal

    average_sessions_per_user: Decimal
    average_session_duration: int

    total_advances_issued: int
    total_advance_amount: Decimal
    credit_builder_cards_active: int

    period_date: date


class GrowthMetrics(BaseModel):
    """Growth metrics over time"""
    date: date
    total_users: int
    new_users: int
    active_users: int
    growth_rate: Decimal  # Percentage


class RevenueMetrics(BaseModel):
    """Revenue metrics"""
    date: date
    mrr: Decimal
    arr: Decimal
    arpu: Decimal  # Average Revenue Per User
    conversion_rate: Decimal


class CohortAnalysis(BaseModel):
    """User cohort analysis"""
    cohort_month: str
    cohort_size: int
    retention_rates: Dict[str, Decimal]  # {"month_1": 80.5, "month_2": 75.2, ...}


# Event Tracking Schemas
class EventLogEntry(BaseModel):
    """Event log entry"""
    id: UUID
    user_id: Optional[UUID] = None
    event_type: str
    event_category: str
    event_name: str
    event_data: Optional[Dict[str, Any]] = None
    service_name: Optional[str] = None
    event_timestamp: datetime


class EventLogCreate(BaseModel):
    """Create event log"""
    user_id: Optional[UUID] = None
    event_type: str = Field(..., description="Type: user_action, system_event, error")
    event_category: str = Field(..., description="Category: engagement, financial, subscription")
    event_name: str
    event_data: Optional[Dict[str, Any]] = None
    service_name: Optional[str] = None


class EventLogFilter(BaseModel):
    """Filter for event logs"""
    user_id: Optional[UUID] = None
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)


# Export Schemas
class ExportRequest(BaseModel):
    """Data export request"""
    export_type: str = Field(..., description="user_data, financial_data, events")
    format: str = Field(default="json", description="json or csv")
    start_date: date
    end_date: date
    filters: Optional[Dict[str, Any]] = None


class ExportResponse(BaseModel):
    """Export response"""
    export_id: UUID
    export_type: str
    format: str
    status: str
    record_count: int
    file_size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    created_at: datetime
