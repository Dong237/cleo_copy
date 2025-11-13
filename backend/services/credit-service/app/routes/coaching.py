"""
Credit coaching and education routes
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import CreditCoachingSession, CreditScore
from app.schemas import (
    CreditCoachingTopic,
    CreditCoachingSessionResponse,
    CreditRecommendation
)


router = APIRouter()


# Coaching content database
COACHING_TOPICS = {
    "credit_utilization": {
        "title": "Understanding Credit Utilization",
        "description": "Learn how credit utilization affects your score and how to optimize it",
        "estimated_time_minutes": 5,
        "estimated_score_impact": 50,
        "content": """
# Understanding Credit Utilization

Credit utilization is the ratio of your credit card balances to your credit limits.

## Why It Matters
- Accounts for 30% of your credit score
- Shows lenders how responsibly you use credit
- Easy to improve quickly

## Optimal Utilization
- Keep total utilization below 30%
- Best scores typically have utilization under 10%
- Pay down balances before statement date

## Quick Tips
1. Pay credit cards multiple times per month
2. Request credit limit increases
3. Keep old cards open (even if unused)
4. Use Cleo's Credit Builder to establish positive history
        """,
        "recommendations": {
            "immediate": [
                "Pay down highest balance cards first",
                "Set up balance alerts at 30% utilization"
            ],
            "short_term": [
                "Request credit limit increases on existing cards",
                "Pay cards before statement closing date"
            ],
            "long_term": [
                "Maintain utilization below 10% for best scores",
                "Keep old accounts open to maintain available credit"
            ]
        }
    },
    "payment_history": {
        "title": "Building Perfect Payment History",
        "description": "Master on-time payments to maximize your credit score",
        "estimated_time_minutes": 5,
        "estimated_score_impact": 100,
        "content": """
# Building Perfect Payment History

Payment history is the single most important factor in your credit score.

## Impact
- Accounts for 35% of your credit score
- Late payments stay on report for 7 years
- Even one late payment can drop score 100+ points

## Payment Timeline
- 0-29 days late: Not reported (but may incur fees)
- 30 days late: Reported to bureaus, major score impact
- 60-90+ days: Increasingly severe impact

## Protection Strategies
1. **Set up autopay** for at least minimum payments
2. **Use calendar reminders** 5 days before due dates
3. **Link multiple payment methods** as backup
4. **Pay early** to build buffer

## With Cleo
- Cleo can remind you before payments are due
- Credit Builder card has automatic payment option
- Get alerts if balance approaches limit
        """,
        "recommendations": {
            "immediate": [
                "Enable autopay on all credit accounts",
                "Set up Cleo payment reminders"
            ],
            "short_term": [
                "Pay all bills at least 3 days early",
                "Check autopay worked each month"
            ],
            "long_term": [
                "Maintain 100% on-time payment history",
                "Never miss a payment for 24+ months"
            ]
        }
    },
    "credit_age": {
        "title": "Building Credit History Length",
        "description": "Strategies to age your credit profile over time",
        "estimated_time_minutes": 4,
        "estimated_score_impact": 30,
        "content": """
# Building Credit History Length

The age of your credit accounts affects your creditworthiness.

## Factors
- Average age of all accounts (15% of score)
- Age of oldest account
- Age of newest account

## Timeline for Impact
- 6 months: Minimum to establish score
- 1 year: Can qualify for better rates
- 2 years: Solid credit history
- 5+ years: Excellent established credit

## Strategies
1. **Keep old accounts open** - even if unused
2. **Use old cards occasionally** - small purchases every 3-6 months
3. **Avoid closing old accounts** - keep them active
4. **Become authorized user** - on parent's/spouse's old account

## What NOT to Do
- Close your oldest credit card
- Apply for many new accounts at once
- Let old cards close due to inactivity
        """,
        "recommendations": {
            "immediate": [
                "Identify your oldest credit account",
                "Make a small purchase on old unused cards"
            ],
            "short_term": [
                "Set up small recurring charge on old cards",
                "Ask to be added as authorized user on parent's card"
            ],
            "long_term": [
                "Keep all accounts open for 7+ years",
                "Space out new account applications (6+ months apart)"
            ]
        }
    },
    "hard_inquiries": {
        "title": "Managing Credit Inquiries",
        "description": "Minimize the impact of credit applications on your score",
        "estimated_time_minutes": 3,
        "estimated_score_impact": 15,
        "content": """
# Managing Credit Inquiries

Credit inquiries are recorded when you apply for credit.

## Types of Inquiries
**Hard Inquiries** (impact score):
- Credit card applications
- Loan applications
- Mortgage applications

**Soft Inquiries** (no impact):
- Checking your own score
- Pre-qualification offers
- Employer checks

## Impact
- Each hard inquiry: 5-10 point drop
- Multiple inquiries: Can indicate risk
- Impact fades after 6 months
- Removed after 2 years

## Rate Shopping Exception
Multiple inquiries for same loan type within 14-45 days count as ONE inquiry:
- Auto loans
- Mortgages
- Student loans

## Best Practices
1. Only apply when necessary
2. Use pre-qualification tools (soft inquiries)
3. Do rate shopping in short window
4. Space out applications by 6+ months
        """,
        "recommendations": {
            "immediate": [
                "Check pre-qualification before applying",
                "Avoid applying for credit unless necessary"
            ],
            "short_term": [
                "Space applications 6+ months apart",
                "Do mortgage/auto rate shopping in 14-day window"
            ],
            "long_term": [
                "Keep inquiries under 2 per year",
                "Focus on building existing credit lines"
            ]
        }
    },
    "credit_mix": {
        "title": "Diversifying Your Credit Mix",
        "description": "How different types of credit accounts affect your score",
        "estimated_time_minutes": 4,
        "estimated_score_impact": 20,
        "content": """
# Diversifying Your Credit Mix

Having different types of credit accounts can boost your score.

## Types of Credit
**Revolving Credit:**
- Credit cards
- Lines of credit
- Store cards

**Installment Credit:**
- Auto loans
- Personal loans
- Student loans
- Mortgages

## Impact
- Accounts for 10% of credit score
- Shows you can manage different credit types
- Not essential, but helpful

## Strategy
1. **Start with secured credit card** (like Cleo Credit Builder)
2. **Add one more revolving account** after 6 months
3. **Consider credit-builder loan** for installment mix
4. **Don't rush into debt** just for credit mix

## With Cleo
- Credit Builder Card: Secured revolving credit
- Credit-builder loan options (coming soon)
- Personalized recommendations based on your profile
        """,
        "recommendations": {
            "immediate": [
                "Ensure you have at least one revolving account",
                "Apply for Cleo Credit Builder if you haven't"
            ],
            "short_term": [
                "Add second credit card after 6 months",
                "Consider small credit-builder loan"
            ],
            "long_term": [
                "Aim for 2-3 credit cards plus 1-2 installment loans",
                "Don't take on debt solely for credit mix"
            ]
        }
    }
}


@router.get("/topics")
async def get_coaching_topics(
    current_user: dict = Depends(get_current_user)
):
    """Get available coaching topics"""

    topics = [
        CreditCoachingTopic(
            topic=key,
            title=value["title"],
            description=value["description"],
            estimated_time_minutes=value["estimated_time_minutes"],
            estimated_score_impact=value["estimated_score_impact"]
        )
        for key, value in COACHING_TOPICS.items()
    ]

    return {
        "topics": topics,
        "total": len(topics)
    }


@router.post("/sessions/{topic}", response_model=CreditCoachingSessionResponse, status_code=201)
async def start_coaching_session(
    topic: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a coaching session on a specific topic"""
    user_id = UUID(current_user["user_id"])

    if topic not in COACHING_TOPICS:
        raise HTTPException(
            status_code=404,
            detail=f"Topic '{topic}' not found. Available: {list(COACHING_TOPICS.keys())}"
        )

    topic_data = COACHING_TOPICS[topic]

    # Create session
    session = CreditCoachingSession(
        user_id=user_id,
        topic=topic,
        content=topic_data["content"],
        recommendations=topic_data["recommendations"],
        completed=False,
        estimated_score_impact=topic_data["estimated_score_impact"]
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return CreditCoachingSessionResponse(
        id=session.id,
        user_id=session.user_id,
        topic=session.topic,
        content=session.content,
        recommendations=session.recommendations,
        completed=session.completed,
        completed_at=session.completed_at,
        estimated_score_impact=session.estimated_score_impact,
        created_at=session.created_at
    )


@router.post("/sessions/{session_id}/complete", response_model=CreditCoachingSessionResponse)
async def complete_coaching_session(
    session_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a coaching session as completed"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(CreditCoachingSession)
        .where(
            CreditCoachingSession.id == session_id,
            CreditCoachingSession.user_id == user_id
        )
    )

    session = result.scalar()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.completed:
        raise HTTPException(status_code=400, detail="Session already completed")

    session.completed = True
    session.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    return CreditCoachingSessionResponse(
        id=session.id,
        user_id=session.user_id,
        topic=session.topic,
        content=session.content,
        recommendations=session.recommendations,
        completed=session.completed,
        completed_at=session.completed_at,
        estimated_score_impact=session.estimated_score_impact,
        created_at=session.created_at
    )


@router.get("/sessions")
async def get_coaching_sessions(
    completed_only: bool = False,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's coaching sessions"""
    user_id = UUID(current_user["user_id"])

    query = select(CreditCoachingSession).where(
        CreditCoachingSession.user_id == user_id
    )

    if completed_only:
        query = query.where(CreditCoachingSession.completed == True)

    query = query.order_by(CreditCoachingSession.created_at.desc())

    result = await db.execute(query)
    sessions = result.scalars().all()

    return {
        "sessions": [
            {
                "id": str(session.id),
                "topic": session.topic,
                "completed": session.completed,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "estimated_score_impact": session.estimated_score_impact,
                "created_at": session.created_at.isoformat()
            }
            for session in sessions
        ],
        "total": len(sessions),
        "completed": sum(1 for s in sessions if s.completed)
    }


@router.get("/recommendations")
async def get_personalized_recommendations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized credit improvement recommendations

    Based on user's current credit profile
    """
    user_id = UUID(current_user["user_id"])

    # Get current credit score
    score_result = await db.execute(
        select(CreditScore)
        .where(CreditScore.user_id == user_id)
        .order_by(CreditScore.checked_at.desc())
        .limit(1)
    )

    score_record = score_result.scalar()

    recommendations = []

    if score_record:
        # Credit utilization recommendation
        if score_record.credit_utilization and score_record.credit_utilization > 30:
            recommendations.append(CreditRecommendation(
                priority="high",
                category="credit_utilization",
                title="Reduce Credit Utilization",
                description=f"Your utilization is {float(score_record.credit_utilization):.1f}%, which is high",
                action_items=[
                    "Pay down credit card balances",
                    "Pay before statement closing date",
                    "Request credit limit increases",
                    "Keep old cards open to maintain available credit"
                ],
                estimated_impact=50,
                estimated_time="1-3 months"
            ))

        # Payment history recommendation
        if score_record.payment_history_score and score_record.payment_history_score < 90:
            recommendations.append(CreditRecommendation(
                priority="high",
                category="payment_history",
                title="Improve Payment History",
                description="Late payments are hurting your score",
                action_items=[
                    "Set up autopay on all accounts",
                    "Pay all bills at least 5 days early",
                    "Use Cleo's payment reminders",
                    "Make 24 consecutive on-time payments"
                ],
                estimated_impact=100,
                estimated_time="6-24 months"
            ))

        # Credit age recommendation
        if score_record.credit_age_months and score_record.credit_age_months < 24:
            recommendations.append(CreditRecommendation(
                priority="medium",
                category="credit_age",
                title="Build Credit History Length",
                description="Your credit history is relatively short",
                action_items=[
                    "Keep all accounts open",
                    "Make small purchases on old unused cards",
                    "Ask to become authorized user on parent's card",
                    "Avoid closing oldest accounts"
                ],
                estimated_impact=30,
                estimated_time="6-24 months"
            ))

        # Hard inquiries recommendation
        if score_record.hard_inquiries and score_record.hard_inquiries > 3:
            recommendations.append(CreditRecommendation(
                priority="medium",
                category="hard_inquiries",
                title="Reduce Credit Applications",
                description=f"You have {score_record.hard_inquiries} recent hard inquiries",
                action_items=[
                    "Stop applying for new credit",
                    "Wait 6 months before next application",
                    "Use pre-qualification tools",
                    "Focus on existing accounts"
                ],
                estimated_impact=15,
                estimated_time="6-12 months"
            ))

        # Account diversity recommendation
        if score_record.total_accounts and score_record.total_accounts < 3:
            recommendations.append(CreditRecommendation(
                priority="low",
                category="credit_mix",
                title="Diversify Credit Mix",
                description="You have limited credit account diversity",
                action_items=[
                    "Apply for Cleo Credit Builder",
                    "Consider a credit-builder loan",
                    "Add one more credit card after 6 months",
                    "Don't rush - quality over quantity"
                ],
                estimated_impact=20,
                estimated_time="12+ months"
            ))

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order[x.priority])

    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "total_potential_impact": sum(r.estimated_impact for r in recommendations)
    }
