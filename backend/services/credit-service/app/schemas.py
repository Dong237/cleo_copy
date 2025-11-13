"""
Pydantic schemas for Credit Service
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# Credit Score Schemas
class CreditScoreResponse(BaseModel):
    """Credit score data"""
    id: UUID
    user_id: UUID
    score: int = Field(..., ge=300, le=850)
    score_provider: str
    score_model: str

    credit_utilization: Optional[Decimal] = None
    payment_history_score: Optional[int] = None
    credit_age_months: Optional[int] = None
    total_accounts: Optional[int] = None
    hard_inquiries: Optional[int] = None

    previous_score: Optional[int] = None
    score_change: Optional[int] = None

    checked_at: datetime

    class Config:
        from_attributes = True


class CreditScoreHistory(BaseModel):
    """Credit score history"""
    scores: List[CreditScoreResponse]
    current_score: int
    highest_score: int
    lowest_score: int
    average_score: int
    trend: str  # improving, declining, stable


class CreditScoreFactor(BaseModel):
    """Credit score factor"""
    factor: str
    impact: str  # positive, negative, neutral
    description: str
    recommendation: str


# Credit Builder Card Schemas
class CreditBuilderCardApplication(BaseModel):
    """Application for credit builder card"""
    security_deposit: Decimal = Field(..., ge=100, le=5000, description="Security deposit ($100-$5000)")
    agree_to_terms: bool = Field(..., description="Must agree to terms")


class CreditBuilderCardResponse(BaseModel):
    """Credit builder card details"""
    id: UUID
    user_id: UUID
    card_number_last4: Optional[str] = None
    status: str
    credit_limit: Decimal
    available_credit: Decimal
    current_balance: Decimal

    security_deposit: Optional[Decimal] = None
    deposit_status: Optional[str] = None

    applied_at: datetime
    approved_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None

    autopay_enabled: bool
    statement_day: int
    due_day: int

    on_time_payments: int
    late_payments: int
    months_active: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditBuilderCardSettings(BaseModel):
    """Update card settings"""
    autopay_enabled: Optional[bool] = None
    statement_day: Optional[int] = Field(None, ge=1, le=28)
    due_day: Optional[int] = Field(None, ge=1, le=28)


class CreditBuilderTransactionResponse(BaseModel):
    """Credit builder transaction"""
    id: UUID
    card_id: UUID
    amount: Decimal
    transaction_type: str
    merchant_name: Optional[str] = None
    category: Optional[str] = None
    status: str
    transaction_date: date
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CreditBuilderPaymentRequest(BaseModel):
    """Payment request"""
    amount: Decimal = Field(..., gt=0)
    payment_type: str = Field(..., description="minimum, full, or custom")
    payment_method: str = Field(default="bank_debit")
    scheduled_date: Optional[date] = None


class CreditBuilderPaymentResponse(BaseModel):
    """Payment details"""
    id: UUID
    card_id: UUID
    amount: Decimal
    payment_type: str
    payment_method: str
    status: str
    due_date: date
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    is_on_time: Optional[bool] = None
    is_autopay: bool

    class Config:
        from_attributes = True


# Credit Coaching Schemas
class CreditCoachingTopic(BaseModel):
    """Available coaching topic"""
    topic: str
    title: str
    description: str
    estimated_time_minutes: int
    estimated_score_impact: int


class CreditCoachingSessionResponse(BaseModel):
    """Coaching session"""
    id: UUID
    user_id: UUID
    topic: str
    content: str
    recommendations: Optional[Dict[str, Any]] = None
    completed: bool
    completed_at: Optional[datetime] = None
    estimated_score_impact: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreditRecommendation(BaseModel):
    """Credit improvement recommendation"""
    priority: str  # high, medium, low
    category: str
    title: str
    description: str
    action_items: List[str]
    estimated_impact: int  # Points
    estimated_time: str


# Alert Schemas
class CreditAlertResponse(BaseModel):
    """Credit alert"""
    id: UUID
    user_id: UUID
    alert_type: str
    severity: str
    title: str
    message: str
    alert_data: Optional[Dict[str, Any]] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CreditAlertUpdate(BaseModel):
    """Update alert status"""
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None


# Credit Report Schemas
class CreditReportAccount(BaseModel):
    """Account on credit report"""
    account_type: str
    creditor: str
    balance: Decimal
    credit_limit: Optional[Decimal] = None
    payment_status: str
    opened_date: date
    months_history: int


class CreditReportSummary(BaseModel):
    """Credit report summary"""
    score: int
    score_provider: str
    report_date: datetime

    # Summary statistics
    total_accounts: int
    open_accounts: int
    closed_accounts: int
    total_balance: Decimal
    total_credit_limit: Decimal
    credit_utilization: Decimal

    # Payment history
    on_time_payments: int
    late_payments: int
    collections: int

    # Inquiries
    hard_inquiries: int
    soft_inquiries: int

    # Age
    oldest_account_months: int
    average_account_age_months: int

    # Recommendations
    recommendations: List[CreditRecommendation]
