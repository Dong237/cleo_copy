"""
Tests for Savings Service
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from decimal import Decimal

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from services.savings_service.main import app


@pytest.fixture
async def authenticated_client():
    """Create authenticated client"""
    return {"Authorization": "Bearer mock-token-for-testing"}


@pytest.fixture
def savings_goal_data():
    """Sample savings goal data"""
    return {
        "name": "Emergency Fund",
        "description": "Save for 6 months of expenses",
        "goal_type": "emergency_fund",
        "target_amount": 10000.00,
        "target_date": (date.today() + timedelta(days=365)).isoformat(),
        "autosave_enabled": True,
        "autosave_amount": 100.00,
        "autosave_frequency": "weekly"
    }


@pytest.mark.asyncio
async def test_create_savings_goal(authenticated_client, savings_goal_data):
    """Test creating a savings goal"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/savings/goals",
            json=savings_goal_data,
            headers=authenticated_client
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == savings_goal_data["name"]
        assert float(data["target_amount"]) == savings_goal_data["target_amount"]
        assert data["autosave_enabled"] == True
        assert "id" in data


@pytest.mark.asyncio
async def test_get_savings_goals(authenticated_client):
    """Test getting all savings goals"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/savings/goals",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "goals" in data
        assert "total" in data
        assert "total_saved" in data
        assert "total_target" in data


@pytest.mark.asyncio
async def test_deposit_to_savings(authenticated_client, savings_goal_data):
    """Test depositing money to savings"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create goal first
        goal_response = await client.post(
            "/api/v1/savings/goals",
            json=savings_goal_data,
            headers=authenticated_client
        )
        goal_id = goal_response.json()["id"]

        # Make deposit
        deposit_data = {
            "goal_id": goal_id,
            "amount": 100.00,
            "method": "manual",
            "description": "Manual savings deposit"
        }
        response = await client.post(
            "/api/v1/savings/transactions/deposit",
            json=deposit_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["amount"]) == 100.00
        assert data["transaction_type"] == "deposit"
        assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_withdraw_from_savings(authenticated_client, savings_goal_data):
    """Test withdrawing money from savings"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create goal and deposit first
        goal_response = await client.post(
            "/api/v1/savings/goals",
            json=savings_goal_data,
            headers=authenticated_client
        )
        goal_id = goal_response.json()["id"]

        await client.post(
            "/api/v1/savings/transactions/deposit",
            json={"goal_id": goal_id, "amount": 100.00},
            headers=authenticated_client
        )

        # Withdraw
        withdrawal_data = {
            "goal_id": goal_id,
            "amount": 50.00,
            "description": "Emergency withdrawal"
        }
        response = await client.post(
            "/api/v1/savings/transactions/withdraw",
            json=withdrawal_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["amount"]) == 50.00
        assert data["transaction_type"] == "withdrawal"


@pytest.mark.asyncio
async def test_get_autosave_settings(authenticated_client):
    """Test getting autosave settings"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/savings/autosave/settings",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "frequency" in data
        assert "estimated_monthly_savings" in data


@pytest.mark.asyncio
async def test_update_autosave_settings(authenticated_client):
    """Test updating autosave settings"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        settings_data = {
            "enabled": True,
            "amount": 50.00,
            "frequency": "weekly"
        }
        response = await client.put(
            "/api/v1/savings/autosave/settings",
            json=settings_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] == True
        assert float(data["amount"]) == 50.00
        assert data["frequency"] == "weekly"


@pytest.mark.asyncio
async def test_get_autosave_recommendation(authenticated_client):
    """Test getting autosave recommendation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/savings/autosave/recommendation",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "recommended_amount" in data
        assert "frequency" in data
        assert "reasoning" in data
        assert "safe_to_save" in data
        assert "projected_monthly_savings" in data


@pytest.mark.asyncio
async def test_savings_goal_progress(authenticated_client, savings_goal_data):
    """Test savings goal includes progress metrics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create goal
        goal_response = await client.post(
            "/api/v1/savings/goals",
            json=savings_goal_data,
            headers=authenticated_client
        )
        goal_id = goal_response.json()["id"]

        # Deposit some money
        await client.post(
            "/api/v1/savings/transactions/deposit",
            json={"goal_id": goal_id, "amount": 1000.00},
            headers=authenticated_client
        )

        # Get goal with progress
        response = await client.get(
            f"/api/v1/savings/goals/{goal_id}",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "percentage_complete" in data
        assert "amount_remaining" in data
        assert "days_remaining" in data
        assert "on_track" in data
        assert data["percentage_complete"] > 0


@pytest.mark.asyncio
async def test_get_savings_transactions(authenticated_client):
    """Test getting savings transaction history"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/savings/transactions",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data
