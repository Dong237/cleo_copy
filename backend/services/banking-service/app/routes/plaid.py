"""
Plaid integration routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import os

import sys
import os as os_module
sys.path.append(os_module.path.join(os_module.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import ExternalServiceException, ValidationException

from app.schemas import (
    PlaidLinkTokenRequest,
    PlaidLinkTokenResponse,
    PlaidExchangeTokenRequest,
    PlaidAccountLinkResponse
)
from app.models import BankAccount

router = APIRouter()

# Plaid configuration
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")


def get_plaid_client():
    """
    Get Plaid client instance
    Note: In production, use the official Plaid Python library
    """
    try:
        from plaid import Client
        from plaid.api import plaid_api

        # This is a placeholder - actual implementation would use plaid-python library
        return {
            "client_id": PLAID_CLIENT_ID,
            "secret": PLAID_SECRET,
            "env": PLAID_ENV
        }
    except ImportError:
        # For development without plaid library installed
        return {
            "client_id": PLAID_CLIENT_ID or "sandbox_client_id",
            "secret": PLAID_SECRET or "sandbox_secret",
            "env": PLAID_ENV
        }


@router.post("/create-link-token", response_model=PlaidLinkTokenResponse)
async def create_link_token(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Plaid Link token for account linking
    """
    try:
        plaid_client = get_plaid_client()

        # In production, this would call Plaid API
        # link_token_response = plaid_client.LinkToken.create({
        #     'user': {'client_user_id': str(current_user["user_id"])},
        #     'client_name': 'Cleo Financial Assistant',
        #     'products': ['auth', 'transactions'],
        #     'country_codes': ['US'],
        #     'language': 'en',
        # })

        # For now, return a mock response
        mock_link_token = f"link-{PLAID_ENV}-{current_user['user_id']}"
        expiration = (datetime.utcnow() + timedelta(hours=4)).isoformat()

        return PlaidLinkTokenResponse(
            link_token=mock_link_token,
            expiration=expiration
        )

    except Exception as e:
        raise ExternalServiceException(f"Failed to create Plaid link token: {str(e)}")


@router.post("/exchange-token", response_model=PlaidAccountLinkResponse)
async def exchange_public_token(
    request: PlaidExchangeTokenRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Exchange Plaid public token for access token and link accounts
    """
    try:
        plaid_client = get_plaid_client()

        # In production, exchange public token for access token
        # exchange_response = plaid_client.Item.public_token.exchange(request.public_token)
        # access_token = exchange_response['access_token']
        # item_id = exchange_response['item_id']

        # Mock response for development
        access_token = f"access-{PLAID_ENV}-mock-token"
        item_id = f"item-{PLAID_ENV}-mock-id"

        # Get accounts from Plaid
        # accounts_response = plaid_client.Accounts.get(access_token)
        # accounts = accounts_response['accounts']

        # Mock accounts for development
        mock_accounts = [
            {
                "account_id": "mock_checking_account_id",
                "name": "Chase Checking",
                "type": "depository",
                "subtype": "checking",
                "balances": {
                    "current": 2500.00,
                    "available": 2500.00
                }
            },
            {
                "account_id": "mock_savings_account_id",
                "name": "Chase Savings",
                "type": "depository",
                "subtype": "savings",
                "balances": {
                    "current": 5000.00,
                    "available": 5000.00
                }
            }
        ]

        # Store accounts in database
        account_ids = []
        for plaid_account in mock_accounts:
            # Check if account already exists
            result = await db.execute(
                select(BankAccount).where(
                    BankAccount.plaid_account_id == plaid_account["account_id"]
                )
            )
            existing_account = result.scalar_one_or_none()

            if not existing_account:
                new_account = BankAccount(
                    user_id=current_user["user_id"],
                    plaid_account_id=plaid_account["account_id"],
                    plaid_item_id=item_id,
                    plaid_access_token=access_token,
                    account_name=plaid_account["name"],
                    account_type=plaid_account["type"],
                    account_subtype=plaid_account.get("subtype"),
                    institution_name="Chase",  # Would come from Plaid institution data
                    current_balance=plaid_account["balances"]["current"],
                    available_balance=plaid_account["balances"]["available"],
                    last_synced_at=datetime.utcnow()
                )
                db.add(new_account)
                await db.flush()
                account_ids.append(new_account.id)
            else:
                account_ids.append(existing_account.id)

        await db.commit()

        return PlaidAccountLinkResponse(
            accounts_linked=len(account_ids),
            account_ids=account_ids,
            message=f"Successfully linked {len(account_ids)} account(s)"
        )

    except Exception as e:
        await db.rollback()
        raise ExternalServiceException(f"Failed to link Plaid accounts: {str(e)}")


@router.post("/refresh/{account_id}")
async def refresh_account(
    account_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh account data from Plaid
    """
    # Get account
    result = await db.execute(
        select(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.user_id == current_user["user_id"]
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        plaid_client = get_plaid_client()

        # In production, fetch fresh data from Plaid
        # balance_response = plaid_client.Accounts.balance.get(account.plaid_access_token)
        # account_data = next(acc for acc in balance_response['accounts']
        #                     if acc['account_id'] == account.plaid_account_id)

        # Mock updated balance
        account.current_balance = 2750.00
        account.available_balance = 2750.00
        account.last_synced_at = datetime.utcnow()
        account.sync_error = None

        await db.commit()

        return {"message": "Account refreshed successfully"}

    except Exception as e:
        account.sync_error = str(e)
        await db.commit()
        raise ExternalServiceException(f"Failed to refresh account: {str(e)}")


@router.delete("/unlink/{item_id}")
async def unlink_institution(
    item_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Unlink institution (remove all accounts from an item)
    """
    # Get all accounts for this item
    result = await db.execute(
        select(BankAccount).where(
            BankAccount.plaid_item_id == item_id,
            BankAccount.user_id == current_user["user_id"]
        )
    )
    accounts = result.scalars().all()

    if not accounts:
        raise HTTPException(status_code=404, detail="Institution not found")

    try:
        # In production, remove item from Plaid
        # plaid_client = get_plaid_client()
        # plaid_client.Item.remove(accounts[0].plaid_access_token)

        # Soft delete accounts (mark as inactive)
        for account in accounts:
            account.is_active = False

        await db.commit()

        return {
            "message": f"Successfully unlinked {len(accounts)} account(s)",
            "accounts_removed": len(accounts)
        }

    except Exception as e:
        await db.rollback()
        raise ExternalServiceException(f"Failed to unlink institution: {str(e)}")
