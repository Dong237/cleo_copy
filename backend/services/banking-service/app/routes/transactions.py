"""
Transaction management routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, desc
from datetime import datetime, timedelta, date
from typing import Optional

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException

from app.schemas import (
    TransactionResponse,
    TransactionListResponse,
    TransactionUpdateRequest,
    TransactionSyncRequest,
    TransactionSyncResponse,
    SpendingAnalytics,
    SpendingByCategory,
    TransactionSearchRequest
)
from app.models import Transaction, BankAccount

router = APIRouter()


@router.get("", response_model=TransactionListResponse)
async def get_transactions(
    account_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    pending: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transactions with filtering and pagination
    """
    query = select(Transaction).where(Transaction.user_id == current_user["user_id"])

    # Apply filters
    if account_id:
        query = query.where(Transaction.account_id == account_id)

    if start_date:
        query = query.where(Transaction.date >= start_date)

    if end_date:
        query = query.where(Transaction.date <= end_date)

    if category:
        query = query.where(
            or_(
                Transaction.category_primary == category,
                Transaction.user_category == category
            )
        )

    if pending is not None:
        query = query.where(Transaction.pending == pending)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(desc(Transaction.date), desc(Transaction.created_at))
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    transactions = result.scalars().all()

    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific transaction details
    """
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user["user_id"]
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise NotFoundException("Transaction not found")

    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update transaction (category, notes, exclusions)
    """
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.id == transaction_id,
                Transaction.user_id == current_user["user_id"]
            )
        )
    )
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise NotFoundException("Transaction not found")

    # Update fields
    if update_data.user_category is not None:
        transaction.user_category = update_data.user_category

    if update_data.user_notes is not None:
        transaction.user_notes = update_data.user_notes

    if update_data.excluded_from_budget is not None:
        transaction.excluded_from_budget = update_data.excluded_from_budget

    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.post("/sync", response_model=TransactionSyncResponse)
async def sync_transactions(
    sync_request: TransactionSyncRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync transactions from Plaid for all or specific accounts
    """
    # Get accounts to sync
    query = select(BankAccount).where(
        and_(
            BankAccount.user_id == current_user["user_id"],
            BankAccount.is_active == True
        )
    )

    if sync_request.account_ids:
        query = query.where(BankAccount.id.in_(sync_request.account_ids))

    result = await db.execute(query)
    accounts = result.scalars().all()

    if not accounts:
        raise NotFoundException("No accounts found to sync")

    # Set date range
    end_date = sync_request.end_date or date.today()
    start_date = sync_request.start_date or (end_date - timedelta(days=30))

    new_count = 0
    updated_count = 0

    for account in accounts:
        try:
            # In production, fetch transactions from Plaid
            # plaid_client = get_plaid_client()
            # transactions_response = plaid_client.Transactions.get(
            #     account.plaid_access_token,
            #     start_date=start_date.isoformat(),
            #     end_date=end_date.isoformat()
            # )

            # Mock transactions for development
            mock_transactions = [
                {
                    "transaction_id": f"mock_txn_1_{account.id}",
                    "amount": -45.50,
                    "date": date.today(),
                    "name": "Starbucks",
                    "merchant_name": "Starbucks",
                    "category": ["Food and Drink", "Restaurants", "Coffee Shop"],
                    "pending": False
                },
                {
                    "transaction_id": f"mock_txn_2_{account.id}",
                    "amount": -120.00,
                    "date": date.today() - timedelta(days=1),
                    "name": "Whole Foods",
                    "merchant_name": "Whole Foods",
                    "category": ["Shops", "Supermarkets and Groceries"],
                    "pending": False
                },
                {
                    "transaction_id": f"mock_txn_3_{account.id}",
                    "amount": 3000.00,
                    "date": date.today() - timedelta(days=2),
                    "name": "Payroll Deposit",
                    "merchant_name": "Employer",
                    "category": ["Income", "Payroll"],
                    "pending": False
                }
            ]

            for plaid_txn in mock_transactions:
                # Check if transaction exists
                txn_result = await db.execute(
                    select(Transaction).where(
                        Transaction.plaid_transaction_id == plaid_txn["transaction_id"]
                    )
                )
                existing_txn = txn_result.scalar_one_or_none()

                if not existing_txn:
                    # Create new transaction
                    new_txn = Transaction(
                        user_id=current_user["user_id"],
                        account_id=account.id,
                        plaid_transaction_id=plaid_txn["transaction_id"],
                        amount=plaid_txn["amount"],
                        date=plaid_txn["date"],
                        merchant_name=plaid_txn.get("merchant_name"),
                        category_primary=plaid_txn["category"][0] if plaid_txn.get("category") else None,
                        category_detailed=plaid_txn["category"][1] if len(plaid_txn.get("category", [])) > 1 else None,
                        description=plaid_txn["name"],
                        pending=plaid_txn.get("pending", False),
                        transaction_type="credit" if plaid_txn["amount"] > 0 else "debit"
                    )
                    db.add(new_txn)
                    new_count += 1
                else:
                    # Update existing transaction if needed
                    if existing_txn.pending and not plaid_txn.get("pending"):
                        existing_txn.pending = False
                        updated_count += 1

            # Update account sync time
            account.last_synced_at = datetime.utcnow()

        except Exception as e:
            account.sync_error = str(e)
            continue

    await db.commit()

    return TransactionSyncResponse(
        synced_count=new_count + updated_count,
        new_transactions=new_count,
        updated_transactions=updated_count,
        accounts_synced=len(accounts),
        message=f"Successfully synced {new_count} new and {updated_count} updated transactions"
    )


@router.get("/analytics/spending", response_model=SpendingAnalytics)
async def get_spending_analytics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get spending analytics and breakdown
    """
    # Default to current month
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = date(end_date.year, end_date.month, 1)

    # Get all transactions in date range
    result = await db.execute(
        select(Transaction).where(
            and_(
                Transaction.user_id == current_user["user_id"],
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.excluded_from_budget == False
            )
        )
    )
    transactions = result.scalars().all()

    # Calculate totals
    total_spent = sum(abs(float(t.amount)) for t in transactions if float(t.amount) < 0)
    total_income = sum(float(t.amount) for t in transactions if float(t.amount) > 0)
    net = total_income - total_spent

    # Group by category
    category_spending = {}
    for txn in transactions:
        if float(txn.amount) < 0:  # Only spending
            category = txn.user_category or txn.category_primary or "Other"
            amount = abs(float(txn.amount))

            if category not in category_spending:
                category_spending[category] = {"amount": 0, "count": 0}

            category_spending[category]["amount"] += amount
            category_spending[category]["count"] += 1

    # Convert to list with percentages
    by_category = [
        SpendingByCategory(
            category=cat,
            amount=data["amount"],
            transaction_count=data["count"],
            percentage=round((data["amount"] / total_spent * 100) if total_spent > 0 else 0, 2)
        )
        for cat, data in sorted(
            category_spending.items(),
            key=lambda x: x[1]["amount"],
            reverse=True
        )
    ]

    # Top merchants
    merchant_spending = {}
    for txn in transactions:
        if float(txn.amount) < 0 and txn.merchant_name:
            merchant = txn.merchant_name
            if merchant not in merchant_spending:
                merchant_spending[merchant] = 0
            merchant_spending[merchant] += abs(float(txn.amount))

    top_merchants = [
        {"merchant": merchant, "amount": amount}
        for merchant, amount in sorted(
            merchant_spending.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    ]

    return SpendingAnalytics(
        total_spent=total_spent,
        total_income=total_income,
        net=net,
        period_start=start_date,
        period_end=end_date,
        by_category=by_category,
        top_merchants=top_merchants
    )


@router.post("/search", response_model=TransactionListResponse)
async def search_transactions(
    search_request: TransactionSearchRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Advanced transaction search
    """
    query = select(Transaction).where(Transaction.user_id == current_user["user_id"])

    # Apply search filters
    if search_request.query:
        search_term = f"%{search_request.query}%"
        query = query.where(
            or_(
                Transaction.merchant_name.ilike(search_term),
                Transaction.description.ilike(search_term),
                Transaction.user_notes.ilike(search_term)
            )
        )

    if search_request.category:
        query = query.where(
            or_(
                Transaction.category_primary == search_request.category,
                Transaction.user_category == search_request.category
            )
        )

    if search_request.min_amount:
        query = query.where(func.abs(Transaction.amount) >= search_request.min_amount)

    if search_request.max_amount:
        query = query.where(func.abs(Transaction.amount) <= search_request.max_amount)

    if search_request.start_date:
        query = query.where(Transaction.date >= search_request.start_date)

    if search_request.end_date:
        query = query.where(Transaction.date <= search_request.end_date)

    if search_request.merchant:
        query = query.where(Transaction.merchant_name.ilike(f"%{search_request.merchant}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (search_request.page - 1) * search_request.page_size
    query = query.order_by(desc(Transaction.date))
    query = query.offset(offset).limit(search_request.page_size)

    result = await db.execute(query)
    transactions = result.scalars().all()

    return TransactionListResponse(
        transactions=transactions,
        total=total,
        page=search_request.page,
        page_size=search_request.page_size
    )
