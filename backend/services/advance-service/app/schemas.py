"""
Pydantic schemas for Advance Service
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


# Eligibility Schemas
class EligibilityCheckResponse(BaseModel):
    """Response for eligibility check"""
    is_eligible: bool
    max_advance_amount: Decimal = Field(..., description="Maximum amount user can request")
    reason: str = Field(..., description="Explanation of eligibility decision")
    check_id: UUID

    # Additional context
    has_regular_income: bool
    income_history_days: int
    has_recent_overdrafts: bool
    average_balance: Decimal
    previous_advance_count: int
    previous_repayment_success_rate: Optional[Decimal] = None

    checked_at: datetime

    class Config:
        from_attributes = True


# Advance Request Schemas
class AdvanceRequest(BaseModel):
    """Request to create a cash advance"""
    amount: Decimal = Field(..., ge=20, le=250, description="Amount to advance ($20-$250)")
    repayment_date: datetime = Field(..., description="When user will repay")
    instant_delivery: bool = Field(default=False, description="Pay $3-5 for instant delivery")
    tip_amount: Decimal = Field(default=Decimal("0.00"), ge=0, le=50, description="Optional tip")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Validate amount is in increments of $5"""
        if v % 5 != 0:
            raise ValueError("Amount must be in $5 increments")
        return v


class AdvanceResponse(BaseModel):
    """Response after creating advance"""
    id: UUID
    user_id: UUID
    amount: Decimal
    status: str

    requested_at: datetime
    repayment_due_date: datetime

    instant_delivery_fee: Decimal
    tip_amount: Decimal
    total_amount: Decimal

    risk_score: Optional[Decimal] = None

    class Config:
        from_attributes = True


class AdvanceDetail(BaseModel):
    """Detailed advance information"""
    id: UUID
    user_id: UUID
    amount: Decimal
    status: str

    requested_at: datetime
    approved_at: Optional[datetime] = None
    disbursed_at: Optional[datetime] = None
    repayment_due_date: datetime
    repaid_at: Optional[datetime] = None

    instant_delivery_fee: Decimal
    tip_amount: Decimal
    total_amount: Decimal

    risk_score: Optional[Decimal] = None
    underwriting_notes: Optional[str] = None

    repayment_status: str
    repayment_attempts: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdvanceListResponse(BaseModel):
    """List of advances"""
    advances: list[AdvanceResponse]
    total: int
    has_active_advance: bool


# Repayment Schemas
class RepaymentScheduleRequest(BaseModel):
    """Request to schedule repayment"""
    advance_id: UUID
    scheduled_date: datetime
    payment_method: str = Field(default="bank_debit")


class RepaymentResponse(BaseModel):
    """Repayment details"""
    id: UUID
    advance_id: UUID
    user_id: UUID
    amount: Decimal
    status: str

    scheduled_date: datetime
    attempted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    payment_method: str
    transaction_id: Optional[str] = None

    failure_reason: Optional[str] = None
    retry_count: int

    created_at: datetime

    class Config:
        from_attributes = True


class RepaymentStatusUpdate(BaseModel):
    """Update repayment status"""
    status: str = Field(..., description="New status: completed, failed")
    transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
