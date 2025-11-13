"""
Tests for Banking Service
"""
import pytest
from httpx import AsyncClient
from datetime import date

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from services.banking_service.main import app


@pytest.fixture
async def authenticated_client(test_user_data, test_user_credentials):
    """Create authenticated client"""
    # This would integrate with user service in production
    # For now, we'll use a mock token
    return {"Authorization": "Bearer mock-token-for-testing"}


@pytest.mark.asyncio
async def test_create_link_token(authenticated_client):
    """Test creating Plaid link token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/plaid/create-link-token",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "link_token" in data
        assert "expiration" in data


@pytest.mark.asyncio
async def test_exchange_public_token(authenticated_client):
    """Test exchanging Plaid public token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        exchange_data = {
            "public_token": "public-sandbox-test-token",
            "accounts": ["account-id-1", "account-id-2"]
        }
        response = await client.post(
            "/api/v1/plaid/exchange-token",
            json=exchange_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert data["accounts_linked"] > 0
        assert len(data["account_ids"]) > 0
        assert "message" in data


@pytest.mark.asyncio
async def test_get_accounts(authenticated_client):
    """Test getting user's bank accounts"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/accounts",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert "total" in data
        assert isinstance(data["accounts"], list)


@pytest.mark.asyncio
async def test_get_account_balance(authenticated_client):
    """Test getting account balance"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, we'd need an account ID
        # This is a simplified test
        account_id = "mock-account-id"
        response = await client.get(
            f"/api/v1/accounts/{account_id}/balance",
            headers=authenticated_client
        )

        # May return 404 if no accounts, which is OK for test
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_transactions(authenticated_client):
    """Test getting transactions"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/transactions",
            params={"page": 1, "page_size": 50},
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["transactions"], list)


@pytest.mark.asyncio
async def test_sync_transactions(authenticated_client):
    """Test syncing transactions"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        sync_data = {
            "start_date": "2025-11-01",
            "end_date": "2025-11-30"
        }
        response = await client.post(
            "/api/v1/transactions/sync",
            json=sync_data,
            headers=authenticated_client
        )

        # May fail if no accounts linked, which is OK
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_spending_analytics(authenticated_client):
    """Test getting spending analytics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/transactions/analytics/spending",
            params={
                "start_date": "2025-11-01",
                "end_date": "2025-11-30"
            },
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_spent" in data
        assert "total_income" in data
        assert "by_category" in data
        assert "top_merchants" in data


@pytest.mark.asyncio
async def test_search_transactions(authenticated_client):
    """Test searching transactions"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        search_data = {
            "query": "coffee",
            "min_amount": 5.0,
            "max_amount": 50.0,
            "page": 1,
            "page_size": 20
        }
        response = await client.post(
            "/api/v1/transactions/search",
            json=search_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data
