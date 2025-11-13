"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import re


class PersonalityMode(str):
    """Personality mode values"""
    FUNNY = "funny"
    SUPPORTIVE = "supportive"
    STRICT = "strict"
    ROAST = "roast"


# Authentication schemas
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


# User schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    phone_number: Optional[str] = None
    profile_photo_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    email_verified: bool
    phone_verified: bool
    personality_mode: str
    notification_enabled: bool
    two_factor_enabled: bool
    subscription_tier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    profile_photo_url: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        return v


# Settings schemas
class PersonalityModeUpdate(BaseModel):
    """Update personality mode"""
    personality_mode: str = Field(..., pattern="^(funny|supportive|strict|roast)$")


class NotificationSettings(BaseModel):
    """Notification settings"""
    notification_enabled: bool


class SubscriptionInfo(BaseModel):
    """Subscription information"""
    subscription_tier: str
    features: list[str]


# Profile schemas
class ProfileResponse(BaseModel):
    """User profile response"""
    id: UUID
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    profile_photo_url: Optional[str]
    personality_mode: str
    subscription_tier: str
    created_at: datetime

    class Config:
        from_attributes = True
