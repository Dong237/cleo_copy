"""
Account management routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException

from app.schemas import (
    AccountResponse,
    AccountListResponse,
    AccountBalanceResponse
)
from app.models import BankAccount

router = APIRouter()


@router.get("", response_model=AccountListResponse)
async def get_accounts(
    active_only: bool = True,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all bank accounts for current user
    """
    query = select(BankAccount).where(BankAccount.user_id == current_user["user_id"])

    if active_only:
        query = query.where(BankAccount.is_active == True)

    result = await db.execute(query.order_by(BankAccount.created_at.desc()))
    accounts = result.scalars().all()

    return AccountListResponse(
        accounts=accounts,
        total=len(accounts)
    )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific bank account details
    """
    result = await db.execute(
        select(BankAccount).where(
            and_(
                BankAccount.id == account_id,
                BankAccount.user_id == current_user["user_id"]
            )
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise NotFoundException("Account not found")

    return account


@router.get("/{account_id}/balance", response_model=AccountBalanceResponse)
async def get_account_balance(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get account balance
    """
    result = await db.execute(
        select(BankAccount).where(
            and_(
                BankAccount.id == account_id,
                BankAccount.user_id == current_user["user_id"]
            )
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise NotFoundException("Account not found")

    return AccountBalanceResponse(
        account_id=account.id,
        current_balance=account.current_balance or 0,
        available_balance=account.available_balance or 0,
        currency=account.currency,
        last_updated=account.last_synced_at
    )


@router.get("/summary/totals")
async def get_account_totals(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get total balance across all accounts
    """
    result = await db.execute(
        select(BankAccount).where(
            and_(
                BankAccount.user_id == current_user["user_id"],
                BankAccount.is_active == True
            )
        )
    )
    accounts = result.scalars().all()

    total_balance = sum(float(acc.current_balance or 0) for acc in accounts)
    total_available = sum(float(acc.available_balance or 0) for acc in accounts)

    # Separate by account type
    checking_balance = sum(
        float(acc.current_balance or 0)
        for acc in accounts
        if acc.account_subtype == "checking"
    )

    savings_balance = sum(
        float(acc.current_balance or 0)
        for acc in accounts
        if acc.account_subtype == "savings"
    )

    return {
        "total_balance": total_balance,
        "total_available": total_available,
        "checking_balance": checking_balance,
        "savings_balance": savings_balance,
        "accounts_count": len(accounts),
        "currency": "USD"
    }


@router.put("/{account_id}/deactivate")
async def deactivate_account(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate an account (soft delete)
    """
    result = await db.execute(
        select(BankAccount).where(
            and_(
                BankAccount.id == account_id,
                BankAccount.user_id == current_user["user_id"]
            )
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise NotFoundException("Account not found")

    account.is_active = False
    await db.commit()

    return {"message": "Account deactivated successfully"}


@router.put("/{account_id}/activate")
async def activate_account(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivate an account
    """
    result = await db.execute(
        select(BankAccount).where(
            and_(
                BankAccount.id == account_id,
                BankAccount.user_id == current_user["user_id"]
            )
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise NotFoundException("Account not found")

    account.is_active = True
    await db.commit()

    return {"message": "Account activated successfully"}
