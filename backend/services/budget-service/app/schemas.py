"""
Pydantic schemas for Budget Service
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# Budget schemas
class BudgetCreate(BaseModel):
    """Create budget request"""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0)
    period: str = Field(default="monthly", pattern="^(weekly|bi-weekly|monthly|yearly)$")
    start_date: date
    end_date: date
    alert_at_75_percent: bool = True
    alert_at_90_percent: bool = True
    alert_at_100_percent: bool = True
    allow_rollover: bool = False

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class BudgetUpdate(BaseModel):
    """Update budget request"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    alert_at_75_percent: Optional[bool] = None
    alert_at_90_percent: Optional[bool] = None
    alert_at_100_percent: Optional[bool] = None
    allow_rollover: Optional[bool] = None


class BudgetResponse(BaseModel):
    """Budget response"""
    id: UUID
    user_id: UUID
    name: str
    category: str
    amount: Decimal
    period: str
    start_date: date
    end_date: date
    is_active: bool
    alert_at_75_percent: bool
    alert_at_90_percent: bool
    alert_at_100_percent: bool
    allow_rollover: bool
    rollover_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class BudgetWithProgress(BudgetResponse):
    """Budget with spending progress"""
    spent: Decimal
    remaining: Decimal
    percentage_used: float
    days_remaining: int
    status: str  # on_track, warning, exceeded


class BudgetListResponse(BaseModel):
    """List of budgets"""
    budgets: List[BudgetWithProgress]
    total: int


# Budget Summary schemas
class CategoryBudgetSummary(BaseModel):
    """Summary for a budget category"""
    category: str
    budget_amount: Decimal
    spent: Decimal
    remaining: Decimal
    percentage_used: float
    status: str


class BudgetSummaryResponse(BaseModel):
    """Overall budget summary"""
    period_start: date
    period_end: date
    total_budget: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    percentage_used: float
    categories: List[CategoryBudgetSummary]
    on_track_count: int
    warning_count: int
    exceeded_count: int


# Alert schemas
class BudgetAlertResponse(BaseModel):
    """Budget alert"""
    id: UUID
    budget_id: UUID
    alert_type: str
    amount_spent: Decimal
    budget_amount: Decimal
    percentage_used: Decimal
    sent_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True


# Analytics schemas
class SpendingTrend(BaseModel):
    """Spending trend over time"""
    date: date
    amount: Decimal


class SpendingComparison(BaseModel):
    """Compare spending across periods"""
    current_period: Decimal
    previous_period: Decimal
    change_amount: Decimal
    change_percentage: float


class BudgetInsight(BaseModel):
    """AI-generated budget insight"""
    insight_type: str  # overspending, underspending, trending_up, etc.
    category: Optional[str]
    message: str
    severity: str  # info, warning, critical
    recommendation: Optional[str]


class BudgetAnalyticsResponse(BaseModel):
    """Comprehensive budget analytics"""
    period_start: date
    period_end: date
    spending_by_day: List[SpendingTrend]
    comparison: SpendingComparison
    insights: List[BudgetInsight]
    top_spending_categories: List[dict]
    budget_adherence_score: float  # 0-100
