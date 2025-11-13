"""
Authentication routes - Registration, login, token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from shared.exceptions import AuthenticationException, ValidationException

from app.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from app.models import User
from sqlalchemy import select

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValidationException("Email already registered")

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login and get access token
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise AuthenticationException("Invalid email or password")

    if not user.is_active:
        raise AuthenticationException("Account is inactive")

    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        payload = decode_token(request.refresh_token)

        if payload.get("type") != "refresh":
            raise AuthenticationException("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")

        # Verify user still exists and is active
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")

        # Create new tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception as e:
        raise AuthenticationException(f"Token refresh failed: {str(e)}")


@router.post("/logout")
async def logout():
    """
    Logout (client should delete tokens)
    """
    return {"message": "Logged out successfully"}
