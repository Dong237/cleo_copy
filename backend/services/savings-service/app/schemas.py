"""
Pydantic schemas for Savings Service
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# Savings Goal schemas
class SavingsGoalCreate(BaseModel):
    """Create savings goal"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    goal_type: Optional[str] = None
    target_amount: Decimal = Field(..., gt=0)
    target_date: Optional[date] = None
    autosave_enabled: bool = False
    autosave_amount: Optional[Decimal] = Field(None, gt=0)
    autosave_frequency: Optional[str] = Field(None, pattern="^(daily|weekly|bi-weekly|monthly)$")


class SavingsGoalUpdate(BaseModel):
    """Update savings goal"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    target_amount: Optional[Decimal] = Field(None, gt=0)
    target_date: Optional[date] = None
    autosave_enabled: Optional[bool] = None
    autosave_amount: Optional[Decimal] = Field(None, gt=0)
    autosave_frequency: Optional[str] = Field(None, pattern="^(daily|weekly|bi-weekly|monthly)$")


class SavingsGoalResponse(BaseModel):
    """Savings goal response"""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    goal_type: Optional[str]
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    target_date: Optional[date]
    started_at: date
    completed_at: Optional[date]
    is_active: bool
    is_completed: bool
    autosave_enabled: bool
    autosave_amount: Optional[Decimal]
    autosave_frequency: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SavingsGoalWithProgress(SavingsGoalResponse):
    """Savings goal with progress metrics"""
    percentage_complete: float
    amount_remaining: Decimal
    days_remaining: Optional[int]
    projected_completion_date: Optional[date]
    on_track: bool


class SavingsGoalListResponse(BaseModel):
    """List of savings goals"""
    goals: List[SavingsGoalWithProgress]
    total: int
    total_saved: Decimal
    total_target: Decimal


# Savings Transaction schemas
class SavingsDepositRequest(BaseModel):
    """Deposit to savings"""
    goal_id: Optional[UUID] = None
    amount: Decimal = Field(..., gt=0)
    method: str = "manual"
    description: Optional[str] = None


class SavingsWithdrawalRequest(BaseModel):
    """Withdraw from savings"""
    goal_id: Optional[UUID] = None
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None


class SavingsTransactionResponse(BaseModel):
    """Savings transaction response"""
    id: UUID
    user_id: UUID
    goal_id: Optional[UUID]
    amount: Decimal
    transaction_type: str
    method: Optional[str]
    status: str
    processed_at: Optional[datetime]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SavingsTransactionListResponse(BaseModel):
    """List of savings transactions"""
    transactions: List[SavingsTransactionResponse]
    total: int


# Autosave schemas
class AutosaveSettingsUpdate(BaseModel):
    """Update autosave settings"""
    enabled: bool
    amount: Optional[Decimal] = Field(None, gt=0)
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|bi-weekly|monthly)$")
    goal_id: Optional[UUID] = None


class AutosaveSettingsResponse(BaseModel):
    """Autosave settings"""
    enabled: bool
    amount: Optional[Decimal]
    frequency: Optional[str]
    goal_id: Optional[UUID]
    next_autosave_date: Optional[date]
    estimated_monthly_savings: Decimal


class AutosaveRecommendation(BaseModel):
    """AI-recommended autosave amount"""
    recommended_amount: Decimal
    frequency: str
    reasoning: str
    safe_to_save: Decimal
    projected_monthly_savings: Decimal
