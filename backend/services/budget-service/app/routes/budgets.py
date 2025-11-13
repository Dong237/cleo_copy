"""
Budget management routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException, ValidationException

from app.schemas import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetWithProgress,
    BudgetListResponse,
    BudgetSummaryResponse,
    CategoryBudgetSummary
)
from app.models import Budget

router = APIRouter()


async def get_budget_spending(user_id: UUID, category: str, start_date: date, end_date: date, db: AsyncSession) -> Decimal:
    """
    Calculate spending for a budget category
    This would query the transactions table in a real implementation
    """
    # Mock spending data for development
    # In production, this would query the transactions service/database
    from random import uniform
    return Decimal(str(round(uniform(50, 500), 2)))


async def calculate_budget_progress(budget: Budget, db: AsyncSession) -> dict:
    """Calculate budget progress and status"""
    user_id = budget.user_id
    spent = await get_budget_spending(user_id, budget.category, budget.start_date, budget.end_date, db)

    remaining = budget.amount - spent
    percentage_used = float(spent / budget.amount * 100) if budget.amount > 0 else 0

    # Calculate days remaining
    days_remaining = (budget.end_date - date.today()).days
    if days_remaining < 0:
        days_remaining = 0

    # Determine status
    if percentage_used >= 100:
        status = "exceeded"
    elif percentage_used >= 90:
        status = "warning"
    else:
        status = "on_track"

    return {
        "spent": spent,
        "remaining": max(remaining, Decimal(0)),
        "percentage_used": round(percentage_used, 2),
        "days_remaining": days_remaining,
        "status": status
    }


@router.post("", response_model=BudgetResponse, status_code=201)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new budget
    """
    # Check for overlapping budgets in same category
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.user_id == current_user["user_id"],
                Budget.category == budget_data.category,
                Budget.is_active == True,
                Budget.start_date <= budget_data.end_date,
                Budget.end_date >= budget_data.start_date
            )
        )
    )
    existing_budget = result.scalar_one_or_none()

    if existing_budget:
        raise ValidationException(
            f"An active budget for '{budget_data.category}' already exists in this period"
        )

    new_budget = Budget(
        user_id=current_user["user_id"],
        name=budget_data.name,
        category=budget_data.category,
        amount=budget_data.amount,
        period=budget_data.period,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        alert_at_75_percent=budget_data.alert_at_75_percent,
        alert_at_90_percent=budget_data.alert_at_90_percent,
        alert_at_100_percent=budget_data.alert_at_100_percent,
        allow_rollover=budget_data.allow_rollover
    )

    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget)

    return new_budget


@router.get("", response_model=BudgetListResponse)
async def get_budgets(
    active_only: bool = True,
    period: Optional[str] = None,  # current, upcoming, past
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all budgets for current user
    """
    query = select(Budget).where(Budget.user_id == current_user["user_id"])

    if active_only:
        query = query.where(Budget.is_active == True)

    # Filter by period
    today = date.today()
    if period == "current":
        query = query.where(
            and_(Budget.start_date <= today, Budget.end_date >= today)
        )
    elif period == "upcoming":
        query = query.where(Budget.start_date > today)
    elif period == "past":
        query = query.where(Budget.end_date < today)

    query = query.order_by(Budget.start_date.desc())

    result = await db.execute(query)
    budgets = result.scalars().all()

    # Add progress information
    budgets_with_progress = []
    for budget in budgets:
        progress = await calculate_budget_progress(budget, db)

        budget_dict = {
            "id": budget.id,
            "user_id": budget.user_id,
            "name": budget.name,
            "category": budget.category,
            "amount": budget.amount,
            "period": budget.period,
            "start_date": budget.start_date,
            "end_date": budget.end_date,
            "is_active": budget.is_active,
            "alert_at_75_percent": budget.alert_at_75_percent,
            "alert_at_90_percent": budget.alert_at_90_percent,
            "alert_at_100_percent": budget.alert_at_100_percent,
            "allow_rollover": budget.allow_rollover,
            "rollover_amount": budget.rollover_amount,
            "created_at": budget.created_at,
            **progress
        }
        budgets_with_progress.append(BudgetWithProgress(**budget_dict))

    return BudgetListResponse(
        budgets=budgets_with_progress,
        total=len(budgets_with_progress)
    )


@router.get("/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get budget summary for a period
    """
    # Default to current month
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1)
    if not end_date:
        end_date = date.today()

    # Get all active budgets in period
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.user_id == current_user["user_id"],
                Budget.is_active == True,
                Budget.start_date <= end_date,
                Budget.end_date >= start_date
            )
        )
    )
    budgets = result.scalars().all()

    total_budget = Decimal(0)
    total_spent = Decimal(0)
    categories = []
    on_track_count = 0
    warning_count = 0
    exceeded_count = 0

    for budget in budgets:
        progress = await calculate_budget_progress(budget, db)

        total_budget += budget.amount
        total_spent += progress["spent"]

        categories.append(CategoryBudgetSummary(
            category=budget.category,
            budget_amount=budget.amount,
            spent=progress["spent"],
            remaining=progress["remaining"],
            percentage_used=progress["percentage_used"],
            status=progress["status"]
        ))

        if progress["status"] == "on_track":
            on_track_count += 1
        elif progress["status"] == "warning":
            warning_count += 1
        else:
            exceeded_count += 1

    total_remaining = total_budget - total_spent
    percentage_used = float(total_spent / total_budget * 100) if total_budget > 0 else 0

    return BudgetSummaryResponse(
        period_start=start_date,
        period_end=end_date,
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=max(total_remaining, Decimal(0)),
        percentage_used=round(percentage_used, 2),
        categories=categories,
        on_track_count=on_track_count,
        warning_count=warning_count,
        exceeded_count=exceeded_count
    )


@router.get("/{budget_id}", response_model=BudgetWithProgress)
async def get_budget(
    budget_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific budget with progress
    """
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.id == budget_id,
                Budget.user_id == current_user["user_id"]
            )
        )
    )
    budget = result.scalar_one_or_none()

    if not budget:
        raise NotFoundException("Budget not found")

    progress = await calculate_budget_progress(budget, db)

    budget_dict = {
        "id": budget.id,
        "user_id": budget.user_id,
        "name": budget.name,
        "category": budget.category,
        "amount": budget.amount,
        "period": budget.period,
        "start_date": budget.start_date,
        "end_date": budget.end_date,
        "is_active": budget.is_active,
        "alert_at_75_percent": budget.alert_at_75_percent,
        "alert_at_90_percent": budget.alert_at_90_percent,
        "alert_at_100_percent": budget.alert_at_100_percent,
        "allow_rollover": budget.allow_rollover,
        "rollover_amount": budget.rollover_amount,
        "created_at": budget.created_at,
        **progress
    }

    return BudgetWithProgress(**budget_dict)


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_update: BudgetUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update budget
    """
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.id == budget_id,
                Budget.user_id == current_user["user_id"]
            )
        )
    )
    budget = result.scalar_one_or_none()

    if not budget:
        raise NotFoundException("Budget not found")

    # Update fields
    if budget_update.name is not None:
        budget.name = budget_update.name
    if budget_update.amount is not None:
        budget.amount = budget_update.amount
    if budget_update.alert_at_75_percent is not None:
        budget.alert_at_75_percent = budget_update.alert_at_75_percent
    if budget_update.alert_at_90_percent is not None:
        budget.alert_at_90_percent = budget_update.alert_at_90_percent
    if budget_update.alert_at_100_percent is not None:
        budget.alert_at_100_percent = budget_update.alert_at_100_percent
    if budget_update.allow_rollover is not None:
        budget.allow_rollover = budget_update.allow_rollover

    await db.commit()
    await db.refresh(budget)

    return budget


@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deactivate) budget
    """
    result = await db.execute(
        select(Budget).where(
            and_(
                Budget.id == budget_id,
                Budget.user_id == current_user["user_id"]
            )
        )
    )
    budget = result.scalar_one_or_none()

    if not budget:
        raise NotFoundException("Budget not found")

    budget.is_active = False
    await db.commit()

    return {"message": "Budget deleted successfully"}
