"""
Savings goals management routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, timedelta
from decimal import Decimal

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException, ValidationException

from app.schemas import (
    SavingsGoalCreate,
    SavingsGoalUpdate,
    SavingsGoalResponse,
    SavingsGoalWithProgress,
    SavingsGoalListResponse
)
from app.models import SavingsGoal, SavingsTransaction

router = APIRouter()


async def calculate_goal_progress(goal: SavingsGoal) -> dict:
    """Calculate progress metrics for a goal"""
    percentage_complete = float(goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
    amount_remaining = goal.target_amount - goal.current_amount

    days_remaining = None
    projected_completion_date = None
    on_track = True

    if goal.target_date:
        days_remaining = (goal.target_date - date.today()).days

        # Calculate if on track
        if days_remaining > 0:
            days_since_start = (date.today() - goal.started_at).days or 1
            current_rate = float(goal.current_amount) / days_since_start
            required_rate = float(amount_remaining) / days_remaining
            on_track = current_rate >= required_rate * 0.9  # 90% of required rate

            # Project completion
            if current_rate > 0:
                days_to_complete = int(float(amount_remaining) / current_rate)
                projected_completion_date = date.today() + timedelta(days=days_to_complete)

    return {
        "percentage_complete": round(percentage_complete, 2),
        "amount_remaining": max(amount_remaining, Decimal(0)),
        "days_remaining": days_remaining,
        "projected_completion_date": projected_completion_date,
        "on_track": on_track
    }


@router.post("", response_model=SavingsGoalResponse, status_code=201)
async def create_goal(
    goal_data: SavingsGoalCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new savings goal"""
    # Validate autosave settings
    if goal_data.autosave_enabled:
        if not goal_data.autosave_amount or not goal_data.autosave_frequency:
            raise ValidationException("Autosave amount and frequency required when autosave is enabled")

    new_goal = SavingsGoal(
        user_id=current_user["user_id"],
        name=goal_data.name,
        description=goal_data.description,
        goal_type=goal_data.goal_type,
        target_amount=goal_data.target_amount,
        target_date=goal_data.target_date,
        autosave_enabled=goal_data.autosave_enabled,
        autosave_amount=goal_data.autosave_amount,
        autosave_frequency=goal_data.autosave_frequency
    )

    db.add(new_goal)
    await db.commit()
    await db.refresh(new_goal)

    return new_goal


@router.get("", response_model=SavingsGoalListResponse)
async def get_goals(
    active_only: bool = True,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all savings goals"""
    query = select(SavingsGoal).where(SavingsGoal.user_id == current_user["user_id"])

    if active_only:
        query = query.where(SavingsGoal.is_active == True, SavingsGoal.is_completed == False)

    query = query.order_by(SavingsGoal.created_at.desc())

    result = await db.execute(query)
    goals = result.scalars().all()

    # Add progress information
    goals_with_progress = []
    for goal in goals:
        progress = await calculate_goal_progress(goal)

        goal_dict = {
            "id": goal.id,
            "user_id": goal.user_id,
            "name": goal.name,
            "description": goal.description,
            "goal_type": goal.goal_type,
            "target_amount": goal.target_amount,
            "current_amount": goal.current_amount,
            "currency": goal.currency,
            "target_date": goal.target_date,
            "started_at": goal.started_at,
            "completed_at": goal.completed_at,
            "is_active": goal.is_active,
            "is_completed": goal.is_completed,
            "autosave_enabled": goal.autosave_enabled,
            "autosave_amount": goal.autosave_amount,
            "autosave_frequency": goal.autosave_frequency,
            "created_at": goal.created_at,
            **progress
        }
        goals_with_progress.append(SavingsGoalWithProgress(**goal_dict))

    total_saved = sum(float(g.current_amount) for g in goals if g.is_active)
    total_target = sum(float(g.target_amount) for g in goals if g.is_active)

    return SavingsGoalListResponse(
        goals=goals_with_progress,
        total=len(goals_with_progress),
        total_saved=Decimal(str(total_saved)),
        total_target=Decimal(str(total_target))
    )


@router.get("/{goal_id}", response_model=SavingsGoalWithProgress)
async def get_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific savings goal"""
    result = await db.execute(
        select(SavingsGoal).where(
            and_(
                SavingsGoal.id == goal_id,
                SavingsGoal.user_id == current_user["user_id"]
            )
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise NotFoundException("Savings goal not found")

    progress = await calculate_goal_progress(goal)

    goal_dict = {
        "id": goal.id,
        "user_id": goal.user_id,
        "name": goal.name,
        "description": goal.description,
        "goal_type": goal.goal_type,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "currency": goal.currency,
        "target_date": goal.target_date,
        "started_at": goal.started_at,
        "completed_at": goal.completed_at,
        "is_active": goal.is_active,
        "is_completed": goal.is_completed,
        "autosave_enabled": goal.autosave_enabled,
        "autosave_amount": goal.autosave_amount,
        "autosave_frequency": goal.autosave_frequency,
        "created_at": goal.created_at,
        **progress
    }

    return SavingsGoalWithProgress(**goal_dict)


@router.put("/{goal_id}", response_model=SavingsGoalResponse)
async def update_goal(
    goal_id: str,
    goal_update: SavingsGoalUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update savings goal"""
    result = await db.execute(
        select(SavingsGoal).where(
            and_(
                SavingsGoal.id == goal_id,
                SavingsGoal.user_id == current_user["user_id"]
            )
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise NotFoundException("Savings goal not found")

    # Update fields
    if goal_update.name is not None:
        goal.name = goal_update.name
    if goal_update.description is not None:
        goal.description = goal_update.description
    if goal_update.target_amount is not None:
        goal.target_amount = goal_update.target_amount
    if goal_update.target_date is not None:
        goal.target_date = goal_update.target_date
    if goal_update.autosave_enabled is not None:
        goal.autosave_enabled = goal_update.autosave_enabled
    if goal_update.autosave_amount is not None:
        goal.autosave_amount = goal_update.autosave_amount
    if goal_update.autosave_frequency is not None:
        goal.autosave_frequency = goal_update.autosave_frequency

    # Check if goal is now complete
    if goal.current_amount >= goal.target_amount and not goal.is_completed:
        goal.is_completed = True
        goal.completed_at = date.today()

    await db.commit()
    await db.refresh(goal)

    return goal


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete (deactivate) savings goal"""
    result = await db.execute(
        select(SavingsGoal).where(
            and_(
                SavingsGoal.id == goal_id,
                SavingsGoal.user_id == current_user["user_id"]
            )
        )
    )
    goal = result.scalar_one_or_none()

    if not goal:
        raise NotFoundException("Savings goal not found")

    goal.is_active = False
    await db.commit()

    return {"message": "Savings goal deleted successfully"}
