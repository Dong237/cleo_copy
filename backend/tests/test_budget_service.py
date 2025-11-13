"""
Tests for Budget Service
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from services.budget_service.main import app


@pytest.fixture
async def authenticated_client():
    """Create authenticated client"""
    return {"Authorization": "Bearer mock-token-for-testing"}


@pytest.fixture
def budget_data():
    """Sample budget data"""
    today = date.today()
    return {
        "name": "Food & Dining",
        "category": "food_dining",
        "amount": 500.00,
        "period": "monthly",
        "start_date": today.replace(day=1).isoformat(),
        "end_date": (today.replace(day=1) + timedelta(days=31)).isoformat()
    }


@pytest.mark.asyncio
async def test_create_budget(authenticated_client, budget_data):
    """Test creating a budget"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/budgets",
            json=budget_data,
            headers=authenticated_client
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == budget_data["name"]
        assert data["category"] == budget_data["category"]
        assert float(data["amount"]) == budget_data["amount"]
        assert "id" in data


@pytest.mark.asyncio
async def test_get_budgets(authenticated_client):
    """Test getting all budgets"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/budgets",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "budgets" in data
        assert "total" in data
        assert isinstance(data["budgets"], list)


@pytest.mark.asyncio
async def test_get_budget_summary(authenticated_client):
    """Test getting budget summary"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/budgets/summary",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_budget" in data
        assert "total_spent" in data
        assert "categories" in data
        assert "on_track_count" in data


@pytest.mark.asyncio
async def test_update_budget(authenticated_client, budget_data):
    """Test updating a budget"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create budget first
        create_response = await client.post(
            "/api/v1/budgets",
            json=budget_data,
            headers=authenticated_client
        )
        budget_id = create_response.json()["id"]

        # Update budget
        update_data = {
            "name": "Updated Food Budget",
            "amount": 600.00
        }
        response = await client.put(
            f"/api/v1/budgets/{budget_id}",
            json=update_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert float(data["amount"]) == update_data["amount"]


@pytest.mark.asyncio
async def test_delete_budget(authenticated_client, budget_data):
    """Test deleting a budget"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create budget first
        create_response = await client.post(
            "/api/v1/budgets",
            json=budget_data,
            headers=authenticated_client
        )
        budget_id = create_response.json()["id"]

        # Delete budget
        response = await client.delete(
            f"/api/v1/budgets/{budget_id}",
            headers=authenticated_client
        )

        assert response.status_code == 200
        assert "message" in response.json()


@pytest.mark.asyncio
async def test_budget_with_progress(authenticated_client, budget_data):
    """Test budget includes progress information"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create budget
        create_response = await client.post(
            "/api/v1/budgets",
            json=budget_data,
            headers=authenticated_client
        )
        budget_id = create_response.json()["id"]

        # Get budget with progress
        response = await client.get(
            f"/api/v1/budgets/{budget_id}",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "spent" in data
        assert "remaining" in data
        assert "percentage_used" in data
        assert "status" in data


@pytest.mark.asyncio
async def test_get_analytics_insights(authenticated_client):
    """Test getting budget analytics"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/analytics/insights",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "spending_by_day" in data
        assert "comparison" in data
        assert "insights" in data
        assert "budget_adherence_score" in data


@pytest.mark.asyncio
async def test_get_recommendations(authenticated_client):
    """Test getting budget recommendations"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/analytics/recommendations",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "total_potential_savings" in data
        assert isinstance(data["recommendations"], list)
