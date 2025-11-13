"""
Pydantic schemas for Banking Service
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# Plaid schemas
class PlaidLinkTokenRequest(BaseModel):
    """Request to create Plaid Link token"""
    user_id: UUID


class PlaidLinkTokenResponse(BaseModel):
    """Plaid Link token response"""
    link_token: str
    expiration: str


class PlaidExchangeTokenRequest(BaseModel):
    """Exchange Plaid public token for access token"""
    public_token: str
    accounts: Optional[List[str]] = None


class PlaidAccountLinkResponse(BaseModel):
    """Response after linking Plaid account"""
    accounts_linked: int
    account_ids: List[UUID]
    message: str


# Account schemas
class AccountBase(BaseModel):
    """Base account schema"""
    account_name: Optional[str] = None
    account_type: str
    account_subtype: Optional[str] = None
    institution_name: Optional[str] = None


class AccountResponse(AccountBase):
    """Account response schema"""
    id: UUID
    user_id: UUID
    current_balance: Optional[Decimal] = None
    available_balance: Optional[Decimal] = None
    currency: str
    is_active: bool
    last_synced_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """List of accounts"""
    accounts: List[AccountResponse]
    total: int


class AccountBalanceResponse(BaseModel):
    """Account balance information"""
    account_id: UUID
    current_balance: Decimal
    available_balance: Decimal
    currency: str
    last_updated: datetime


# Transaction schemas
class TransactionBase(BaseModel):
    """Base transaction schema"""
    amount: Decimal
    merchant_name: Optional[str] = None
    category_primary: Optional[str] = None
    date: date
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Transaction response schema"""
    id: UUID
    account_id: UUID
    merchant_logo_url: Optional[str] = None
    category_detailed: Optional[str] = None
    user_category: Optional[str] = None
    user_notes: Optional[str] = None
    pending: bool
    transaction_type: Optional[str] = None
    excluded_from_budget: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """List of transactions"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int


class TransactionUpdateRequest(BaseModel):
    """Update transaction"""
    user_category: Optional[str] = None
    user_notes: Optional[str] = None
    excluded_from_budget: Optional[bool] = None


class TransactionSyncRequest(BaseModel):
    """Sync transactions for accounts"""
    account_ids: Optional[List[UUID]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TransactionSyncResponse(BaseModel):
    """Transaction sync response"""
    synced_count: int
    new_transactions: int
    updated_transactions: int
    accounts_synced: int
    message: str


# Analytics schemas
class SpendingByCategory(BaseModel):
    """Spending breakdown by category"""
    category: str
    amount: Decimal
    transaction_count: int
    percentage: float


class SpendingAnalytics(BaseModel):
    """Spending analytics"""
    total_spent: Decimal
    total_income: Decimal
    net: Decimal
    period_start: date
    period_end: date
    by_category: List[SpendingByCategory]
    top_merchants: List[dict]


class TransactionSearchRequest(BaseModel):
    """Search transactions"""
    query: Optional[str] = None
    category: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    merchant: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)
