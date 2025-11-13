"""
Tests for User Service - Authentication
"""
import pytest
from httpx import AsyncClient

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from services.user_service.main import app


@pytest.mark.asyncio
async def test_register_user(test_user_data):
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password


@pytest.mark.asyncio
async def test_register_duplicate_email(test_user_data):
    """Test registering with duplicate email"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register again with same email
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 422
        assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password():
    """Test registration with weak password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        weak_password_data = {
            "email": "test@example.com",
            "password": "weak",  # No numbers, too short
            "first_name": "Test"
        }
        response = await client.post("/api/v1/auth/register", json=weak_password_data)

        assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(test_user_data, test_user_credentials):
    """Test successful login"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        response = await client.post("/api/v1/auth/login", json=test_user_credentials)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(test_user_data):
    """Test login with wrong password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post("/api/v1/auth/register", json=test_user_data)

        # Try to login with wrong password
        wrong_credentials = {
            "email": test_user_data["email"],
            "password": "WrongPassword123"
        }
        response = await client.post("/api/v1/auth/login", json=wrong_credentials)

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user():
    """Test login with non-existent user"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        credentials = {
            "email": "nonexistent@example.com",
            "password": "Password123"
        }
        response = await client.post("/api/v1/auth/login", json=credentials)

        assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(test_user_data, test_user_credentials):
    """Test token refresh"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_credentials)
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_current_user(test_user_data, test_user_credentials):
    """Test getting current user info"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_credentials)
        access_token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]


@pytest.mark.asyncio
async def test_update_user_profile(test_user_data, test_user_credentials):
    """Test updating user profile"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_credentials)
        access_token = login_response.json()["access_token"]

        # Update profile
        update_data = {
            "first_name": "Updated",
            "phone_number": "+1234567890"
        }
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["phone_number"] == "+1234567890"


@pytest.mark.asyncio
async def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 403  # Forbidden or 401 Unauthorized


@pytest.mark.asyncio
async def test_change_password(test_user_data, test_user_credentials):
    """Test changing password"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_credentials)
        access_token = login_response.json()["access_token"]

        # Change password
        password_change = {
            "current_password": test_user_data["password"],
            "new_password": "NewSecurePass456"
        }
        response = await client.post(
            "/api/v1/users/me/change-password",
            json=password_change,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200

        # Try to login with new password
        new_credentials = {
            "email": test_user_data["email"],
            "password": "NewSecurePass456"
        }
        login_response = await client.post("/api/v1/auth/login", json=new_credentials)
        assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_update_personality_mode(test_user_data, test_user_credentials):
    """Test updating personality mode"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await client.post("/api/v1/auth/login", json=test_user_credentials)
        access_token = login_response.json()["access_token"]

        # Update personality
        response = await client.put(
            "/api/v1/users/me/personality",
            json={"personality_mode": "roast"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["personality_mode"] == "roast"
