"""
Savings transactions routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import datetime, date

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException, ValidationException

from app.schemas import (
    SavingsDepositRequest,
    SavingsWithdrawalRequest,
    SavingsTransactionResponse,
    SavingsTransactionListResponse
)
from app.models import SavingsGoal, SavingsTransaction

router = APIRouter()


@router.post("/deposit", response_model=SavingsTransactionResponse)
async def deposit_to_savings(
    deposit_data: SavingsDepositRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deposit money to savings"""
    # Verify goal exists if goal_id provided
    if deposit_data.goal_id:
        result = await db.execute(
            select(SavingsGoal).where(
                and_(
                    SavingsGoal.id == deposit_data.goal_id,
                    SavingsGoal.user_id == current_user["user_id"]
                )
            )
        )
        goal = result.scalar_one_or_none()

        if not goal:
            raise NotFoundException("Savings goal not found")

        # Update goal amount
        goal.current_amount += deposit_data.amount

        # Check if goal is complete
        if goal.current_amount >= goal.target_amount and not goal.is_completed:
            goal.is_completed = True
            goal.completed_at = date.today()

    # Create transaction
    transaction = SavingsTransaction(
        user_id=current_user["user_id"],
        goal_id=deposit_data.goal_id,
        amount=deposit_data.amount,
        transaction_type="deposit",
        method=deposit_data.method,
        status="completed",
        processed_at=datetime.utcnow(),
        description=deposit_data.description
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.post("/withdraw", response_model=SavingsTransactionResponse)
async def withdraw_from_savings(
    withdrawal_data: SavingsWithdrawalRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Withdraw money from savings"""
    # Verify goal exists and has sufficient funds
    if withdrawal_data.goal_id:
        result = await db.execute(
            select(SavingsGoal).where(
                and_(
                    SavingsGoal.id == withdrawal_data.goal_id,
                    SavingsGoal.user_id == current_user["user_id"]
                )
            )
        )
        goal = result.scalar_one_or_none()

        if not goal:
            raise NotFoundException("Savings goal not found")

        if goal.current_amount < withdrawal_data.amount:
            raise ValidationException("Insufficient funds in savings goal")

        # Update goal amount
        goal.current_amount -= withdrawal_data.amount

        # Mark as not completed if it was
        if goal.is_completed:
            goal.is_completed = False
            goal.completed_at = None

    # Create transaction
    transaction = SavingsTransaction(
        user_id=current_user["user_id"],
        goal_id=withdrawal_data.goal_id,
        amount=withdrawal_data.amount,
        transaction_type="withdrawal",
        method="manual",
        status="completed",
        processed_at=datetime.utcnow(),
        description=withdrawal_data.description
    )

    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.get("", response_model=SavingsTransactionListResponse)
async def get_savings_transactions(
    goal_id: str = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get savings transaction history"""
    query = select(SavingsTransaction).where(
        SavingsTransaction.user_id == current_user["user_id"]
    )

    if goal_id:
        query = query.where(SavingsTransaction.goal_id == goal_id)

    query = query.order_by(desc(SavingsTransaction.created_at)).limit(limit)

    result = await db.execute(query)
    transactions = result.scalars().all()

    return SavingsTransactionListResponse(
        transactions=transactions,
        total=len(transactions)
    )
