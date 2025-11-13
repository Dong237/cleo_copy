"""
Credit builder card routes
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth import get_current_user
from database import get_db
from app.models import (
    CreditBuilderCard,
    CreditBuilderTransaction,
    CreditBuilderPayment
)
from app.schemas import (
    CreditBuilderCardApplication,
    CreditBuilderCardResponse,
    CreditBuilderCardSettings,
    CreditBuilderTransactionResponse,
    CreditBuilderPaymentRequest,
    CreditBuilderPaymentResponse
)


router = APIRouter()


@router.post("/apply", response_model=CreditBuilderCardResponse, status_code=201)
async def apply_for_card(
    application: CreditBuilderCardApplication,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Apply for credit builder card

    Requirements:
    - Security deposit ($100-$5000)
    - Agree to terms
    - No existing card
    """
    user_id = UUID(current_user["user_id"])

    # Check for existing card
    result = await db.execute(
        select(CreditBuilderCard)
        .where(CreditBuilderCard.user_id == user_id)
    )

    existing_card = result.scalar()

    if existing_card:
        raise HTTPException(
            status_code=400,
            detail="You already have a credit builder card"
        )

    if not application.agree_to_terms:
        raise HTTPException(
            status_code=400,
            detail="You must agree to terms and conditions"
        )

    # Create card with security deposit as credit limit
    card = CreditBuilderCard(
        user_id=user_id,
        status="active",  # Auto-approve for eligible users
        credit_limit=application.security_deposit,
        available_credit=application.security_deposit,
        current_balance=Decimal("0.00"),
        security_deposit=application.security_deposit,
        deposit_status="held",
        approved_at=datetime.utcnow(),
        activated_at=datetime.utcnow()
    )

    db.add(card)
    await db.commit()
    await db.refresh(card)

    print(f"💳 Credit builder card approved for user {user_id}")
    print(f"   Credit limit: ${card.credit_limit}")

    return CreditBuilderCardResponse(
        id=card.id,
        user_id=card.user_id,
        card_number_last4=card.card_number_last4,
        status=card.status,
        credit_limit=card.credit_limit,
        available_credit=card.available_credit,
        current_balance=card.current_balance,
        security_deposit=card.security_deposit,
        deposit_status=card.deposit_status,
        applied_at=card.applied_at,
        approved_at=card.approved_at,
        activated_at=card.activated_at,
        autopay_enabled=card.autopay_enabled,
        statement_day=card.statement_day,
        due_day=card.due_day,
        on_time_payments=card.on_time_payments,
        late_payments=card.late_payments,
        months_active=card.months_active,
        created_at=card.created_at,
        updated_at=card.updated_at
    )


@router.get("/card", response_model=CreditBuilderCardResponse)
async def get_card(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's credit builder card"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(CreditBuilderCard)
        .where(CreditBuilderCard.user_id == user_id)
    )

    card = result.scalar()

    if not card:
        raise HTTPException(
            status_code=404,
            detail="No credit builder card found. Apply for one first!"
        )

    return CreditBuilderCardResponse(
        id=card.id,
        user_id=card.user_id,
        card_number_last4=card.card_number_last4,
        status=card.status,
        credit_limit=card.credit_limit,
        available_credit=card.available_credit,
        current_balance=card.current_balance,
        security_deposit=card.security_deposit,
        deposit_status=card.deposit_status,
        applied_at=card.applied_at,
        approved_at=card.approved_at,
        activated_at=card.activated_at,
        autopay_enabled=card.autopay_enabled,
        statement_day=card.statement_day,
        due_day=card.due_day,
        on_time_payments=card.on_time_payments,
        late_payments=card.late_payments,
        months_active=card.months_active,
        created_at=card.created_at,
        updated_at=card.updated_at
    )


@router.patch("/card/settings", response_model=CreditBuilderCardResponse)
async def update_card_settings(
    settings: CreditBuilderCardSettings,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update credit builder card settings"""
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(CreditBuilderCard)
        .where(CreditBuilderCard.user_id == user_id)
    )

    card = result.scalar()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Update settings
    if settings.autopay_enabled is not None:
        card.autopay_enabled = settings.autopay_enabled

    if settings.statement_day is not None:
        card.statement_day = settings.statement_day

    if settings.due_day is not None:
        if settings.due_day <= (settings.statement_day or card.statement_day):
            raise HTTPException(
                status_code=400,
                detail="Due day must be after statement day"
            )
        card.due_day = settings.due_day

    card.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(card)

    return CreditBuilderCardResponse(
        id=card.id,
        user_id=card.user_id,
        card_number_last4=card.card_number_last4,
        status=card.status,
        credit_limit=card.credit_limit,
        available_credit=card.available_credit,
        current_balance=card.current_balance,
        security_deposit=card.security_deposit,
        deposit_status=card.deposit_status,
        applied_at=card.applied_at,
        approved_at=card.approved_at,
        activated_at=card.activated_at,
        autopay_enabled=card.autopay_enabled,
        statement_day=card.statement_day,
        due_day=card.due_day,
        on_time_payments=card.on_time_payments,
        late_payments=card.late_payments,
        months_active=card.months_active,
        created_at=card.created_at,
        updated_at=card.updated_at
    )


@router.get("/transactions")
async def get_transactions(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get credit builder card transactions"""
    user_id = UUID(current_user["user_id"])

    # Get card
    card_result = await db.execute(
        select(CreditBuilderCard)
        .where(CreditBuilderCard.user_id == user_id)
    )

    card = card_result.scalar()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Get transactions
    result = await db.execute(
        select(CreditBuilderTransaction)
        .where(CreditBuilderTransaction.card_id == card.id)
        .order_by(CreditBuilderTransaction.transaction_date.desc())
        .limit(limit)
    )

    transactions = result.scalars().all()

    return {
        "transactions": [
            {
                "id": str(txn.id),
                "amount": float(txn.amount),
                "transaction_type": txn.transaction_type,
                "merchant_name": txn.merchant_name,
                "category": txn.category,
                "status": txn.status,
                "transaction_date": txn.transaction_date.isoformat(),
                "description": txn.description
            }
            for txn in transactions
        ],
        "total": len(transactions)
    }


@router.post("/payments", response_model=CreditBuilderPaymentResponse, status_code=201)
async def make_payment(
    payment: CreditBuilderPaymentRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Make payment on credit builder card

    Payment types:
    - minimum: Pay minimum amount (typically 2% of balance or $25)
    - full: Pay full balance
    - custom: Pay custom amount
    """
    user_id = UUID(current_user["user_id"])

    # Get card
    result = await db.execute(
        select(CreditBuilderCard)
        .where(CreditBuilderCard.user_id == user_id)
    )

    card = result.scalar()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if card.current_balance == Decimal("0.00"):
        raise HTTPException(
            status_code=400,
            detail="No balance to pay"
        )

    # Validate payment amount
    if payment.payment_type == "minimum":
        min_payment = max(card.current_balance * Decimal("0.02"), Decimal("25.00"))
        if payment.amount < min_payment:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum payment is ${min_payment}"
            )
    elif payment.payment_type == "full":
        if payment.amount != card.current_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Full balance is ${card.current_balance}"
            )
    elif payment.payment_type == "custom":
        if payment.amount > card.current_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Payment cannot exceed balance of ${card.current_balance}"
            )

    # Determine due date (next statement due date)
    today = date.today()
    if today.day < card.due_day:
        due_date = date(today.year, today.month, card.due_day)
    else:
        # Next month
        next_month = today.month + 1
        year = today.year
        if next_month > 12:
            next_month = 1
            year += 1
        due_date = date(year, next_month, card.due_day)

    # Create payment
    payment_record = CreditBuilderPayment(
        card_id=card.id,
        user_id=user_id,
        amount=payment.amount,
        payment_type=payment.payment_type,
        payment_method=payment.payment_method,
        status="completed",  # Auto-complete for development
        is_autopay=False,
        due_date=due_date,
        scheduled_date=payment.scheduled_date or date.today(),
        completed_date=date.today(),
        is_on_time=True,
        days_late=0
    )

    db.add(payment_record)

    # Update card balance
    card.current_balance -= payment.amount
    card.available_credit += payment.amount
    card.on_time_payments += 1
    card.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(payment_record)

    print(f"💰 Payment processed for card {card.id}: ${payment.amount}")

    return CreditBuilderPaymentResponse(
        id=payment_record.id,
        card_id=payment_record.card_id,
        amount=payment_record.amount,
        payment_type=payment_record.payment_type,
        payment_method=payment_record.payment_method,
        status=payment_record.status,
        due_date=payment_record.due_date,
        scheduled_date=payment_record.scheduled_date,
        completed_date=payment_record.completed_date,
        is_on_time=payment_record.is_on_time,
        is_autopay=payment_record.is_autopay
    )


@router.get("/payments")
async def get_payments(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment history"""
    user_id = UUID(current_user["user_id"])

    # Get card
    card_result = await db.execute(
        select(CreditBuilderCard)
        .where(CreditBuilderCard.user_id == user_id)
    )

    card = card_result.scalar()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Get payments
    result = await db.execute(
        select(CreditBuilderPayment)
        .where(CreditBuilderPayment.card_id == card.id)
        .order_by(CreditBuilderPayment.created_at.desc())
        .limit(limit)
    )

    payments = result.scalars().all()

    return {
        "payments": [
            {
                "id": str(payment.id),
                "amount": float(payment.amount),
                "payment_type": payment.payment_type,
                "status": payment.status,
                "due_date": payment.due_date.isoformat(),
                "completed_date": payment.completed_date.isoformat() if payment.completed_date else None,
                "is_on_time": payment.is_on_time,
                "is_autopay": payment.is_autopay
            }
            for payment in payments
        ],
        "total": len(payments)
    }


@router.post("/card/close")
async def close_card(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Close credit builder card

    Requirements:
    - Zero balance
    - Account will be reported to credit bureaus
    - Security deposit will be returned
    """
    user_id = UUID(current_user["user_id"])

    result = await db.execute(
        select(CreditBuilderCard)
        .where(CreditBuilderCard.user_id == user_id)
    )

    card = result.scalar()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if card.status == "closed":
        raise HTTPException(status_code=400, detail="Card is already closed")

    if card.current_balance > Decimal("0.00"):
        raise HTTPException(
            status_code=400,
            detail=f"Must pay off balance of ${card.current_balance} before closing"
        )

    # Close card
    card.status = "closed"
    card.closed_at = datetime.utcnow()
    card.deposit_status = "returned"
    card.updated_at = datetime.utcnow()

    await db.commit()

    print(f"🔒 Credit builder card closed for user {user_id}")

    return {
        "message": "Card closed successfully",
        "security_deposit_returned": float(card.security_deposit),
        "months_active": card.months_active,
        "on_time_payments": card.on_time_payments
    }
