"""
Credit report routes
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import CreditScore
from app.schemas import (
    CreditReportAccount,
    CreditReportSummary,
    CreditRecommendation
)


router = APIRouter()


@router.get("/summary", response_model=CreditReportSummary)
async def get_credit_report_summary(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive credit report summary

    In production, this would fetch full credit report from bureau
    """
    user_id = UUID(current_user["user_id"])

    # Get current score
    score_result = await db.execute(
        select(CreditScore)
        .where(CreditScore.user_id == user_id)
        .order_by(CreditScore.checked_at.desc())
        .limit(1)
    )

    score_record = score_result.scalar()

    if not score_record:
        raise HTTPException(
            status_code=404,
            detail="No credit score found. Check your credit first."
        )

    # Generate mock report data (in production, fetch from credit bureau)
    total_accounts = score_record.total_accounts or 5
    open_accounts = random.randint(2, total_accounts)
    closed_accounts = total_accounts - open_accounts

    total_balance = Decimal(str(random.randint(2000, 10000)))
    total_limit = Decimal(str(random.randint(10000, 30000)))
    utilization = (total_balance / total_limit * 100) if total_limit > 0 else Decimal("0")

    on_time_payments = random.randint(20, 50)
    late_payments = random.randint(0, 3)

    # Generate recommendations based on profile
    recommendations = _generate_recommendations(score_record)

    return CreditReportSummary(
        score=score_record.score,
        score_provider=score_record.score_provider,
        report_date=score_record.checked_at,
        total_accounts=total_accounts,
        open_accounts=open_accounts,
        closed_accounts=closed_accounts,
        total_balance=total_balance,
        total_credit_limit=total_limit,
        credit_utilization=utilization,
        on_time_payments=on_time_payments,
        late_payments=late_payments,
        collections=0,
        hard_inquiries=score_record.hard_inquiries or 0,
        soft_inquiries=random.randint(5, 15),
        oldest_account_months=score_record.credit_age_months or 24,
        average_account_age_months=(score_record.credit_age_months or 24) // 2,
        recommendations=recommendations
    )


@router.get("/accounts")
async def get_credit_report_accounts(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed account information from credit report

    In production, this would fetch from credit bureau
    """
    user_id = UUID(current_user["user_id"])

    # Get current score to verify user has credit data
    score_result = await db.execute(
        select(CreditScore)
        .where(CreditScore.user_id == user_id)
        .order_by(CreditScore.checked_at.desc())
        .limit(1)
    )

    score_record = score_result.scalar()

    if not score_record:
        raise HTTPException(
            status_code=404,
            detail="No credit data found"
        )

    # Generate mock account data
    accounts = []

    # Mock credit cards
    credit_cards = [
        {
            "creditor": "Chase Bank",
            "balance": Decimal("1500.00"),
            "credit_limit": Decimal("5000.00"),
            "months_history": 36
        },
        {
            "creditor": "American Express",
            "balance": Decimal("800.00"),
            "credit_limit": Decimal("10000.00"),
            "months_history": 24
        },
        {
            "creditor": "Cleo Credit Builder",
            "balance": Decimal("0.00"),
            "credit_limit": Decimal("500.00"),
            "months_history": 6
        }
    ]

    for card in credit_cards[:score_record.total_accounts or 3]:
        accounts.append(CreditReportAccount(
            account_type="Credit Card",
            creditor=card["creditor"],
            balance=card["balance"],
            credit_limit=card["credit_limit"],
            payment_status="Current",
            opened_date=date.today() - timedelta(days=card["months_history"] * 30),
            months_history=card["months_history"]
        ))

    # Mock installment loan (if applicable)
    if (score_record.total_accounts or 0) > 3:
        accounts.append(CreditReportAccount(
            account_type="Auto Loan",
            creditor="Wells Fargo Auto",
            balance=Decimal("12000.00"),
            credit_limit=None,
            payment_status="Current",
            opened_date=date.today() - timedelta(days=18 * 30),
            months_history=18
        ))

    return {
        "accounts": accounts,
        "total": len(accounts),
        "open_accounts": len([a for a in accounts if a.balance > 0]),
        "total_balance": float(sum(a.balance for a in accounts)),
        "total_credit_limit": float(sum(a.credit_limit for a in accounts if a.credit_limit))
    }


@router.get("/disputes")
async def get_dispute_options(
    current_user: dict = Depends(get_current_user)
):
    """
    Get information about disputing credit report items

    In production, would integrate with bureau dispute process
    """
    return {
        "can_dispute": True,
        "dispute_reasons": [
            "Not my account",
            "Account information inaccurate",
            "Fraudulent account",
            "Payment marked late but was on time",
            "Account already paid",
            "Duplicate account"
        ],
        "process": [
            "Identify inaccurate information on your report",
            "Gather supporting documentation",
            "Submit dispute through Cleo or directly to bureau",
            "Bureau investigates within 30 days",
            "Receive results and updated report"
        ],
        "note": "Disputing accurate information will not help your score. Focus on building positive payment history instead."
    }


def _generate_recommendations(score_record: CreditScore) -> list[CreditRecommendation]:
    """Generate personalized recommendations based on credit profile"""
    recommendations = []

    # Check utilization
    if score_record.credit_utilization and score_record.credit_utilization > 30:
        recommendations.append(CreditRecommendation(
            priority="high",
            category="credit_utilization",
            title="Lower Credit Card Balances",
            description=f"Utilization at {float(score_record.credit_utilization):.1f}% is impacting your score",
            action_items=[
                f"Pay down balances to get under 30% utilization",
                "Consider paying credit cards twice per month",
                "Request credit limit increases to lower utilization ratio"
            ],
            estimated_impact=50,
            estimated_time="1-2 months"
        ))

    # Check payment history
    if score_record.payment_history_score and score_record.payment_history_score < 85:
        recommendations.append(CreditRecommendation(
            priority="high",
            category="payment_history",
            title="Build Perfect Payment Record",
            description="Payment history is the #1 factor in your credit score",
            action_items=[
                "Enable autopay on all credit accounts",
                "Set up Cleo payment reminders",
                "Pay bills 5+ days before due date"
            ],
            estimated_impact=100,
            estimated_time="12-24 months"
        ))

    # Check credit age
    if score_record.credit_age_months and score_record.credit_age_months < 24:
        recommendations.append(CreditRecommendation(
            priority="medium",
            category="credit_age",
            title="Establish Longer Credit History",
            description="Your average account age is less than 2 years",
            action_items=[
                "Keep your oldest credit accounts open",
                "Avoid closing accounts",
                "Consider becoming an authorized user on a parent's old account"
            ],
            estimated_impact=30,
            estimated_time="12+ months"
        ))

    # Check total accounts
    if score_record.total_accounts and score_record.total_accounts < 3:
        recommendations.append(CreditRecommendation(
            priority="low",
            category="credit_mix",
            title="Add Account Diversity",
            description="Having multiple types of credit can help your score",
            action_items=[
                "Apply for Cleo Credit Builder if you haven't",
                "Consider adding one more credit card after 6+ months",
                "Maintain mix of revolving and installment credit"
            ],
            estimated_impact=20,
            estimated_time="6-12 months"
        ))

    return recommendations
