"""
Database models for Banking Service
"""
from sqlalchemy import Column, String, Boolean, Numeric, ForeignKey, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from shared.database import Base
from shared.models import TimestampMixin


class BankAccount(Base, TimestampMixin):
    """Bank Account model"""

    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Plaid information
    plaid_account_id = Column(String(255), unique=True, nullable=False)
    plaid_item_id = Column(String(255), nullable=False, index=True)
    plaid_access_token = Column(Text, nullable=False)

    # Account details
    account_name = Column(String(255))
    account_type = Column(String(50))  # checking, savings, credit
    account_subtype = Column(String(50))
    institution_name = Column(String(255))
    institution_id = Column(String(255))

    # Balance information
    current_balance = Column(Numeric(12, 2))
    available_balance = Column(Numeric(12, 2))
    currency = Column(String(3), default="USD")

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_synced_at = Column(DateTime(timezone=True))
    sync_error = Column(Text)

    def __repr__(self):
        return f"<BankAccount(id={self.id}, account_name={self.account_name})>"


class Transaction(Base, TimestampMixin):
    """Transaction model"""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Plaid transaction data
    plaid_transaction_id = Column(String(255), unique=True)

    # Transaction details
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    date = Column(Date, nullable=False, index=True)
    authorized_date = Column(Date)

    # Merchant information
    merchant_name = Column(String(255), index=True)
    merchant_logo_url = Column(String(500))

    # Categorization
    category_primary = Column(String(100), index=True)
    category_detailed = Column(String(100))

    # Transaction metadata
    description = Column(Text)
    pending = Column(Boolean, default=False)
    transaction_type = Column(String(50))  # debit, credit

    # User customization
    user_category = Column(String(100), index=True)
    user_notes = Column(Text)
    excluded_from_budget = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, merchant={self.merchant_name})>"
