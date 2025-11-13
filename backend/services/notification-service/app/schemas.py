"""
Pydantic schemas for Notification Service
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# Notification schemas
class NotificationCreate(BaseModel):
    """Create notification request"""
    user_id: UUID
    type: str = Field(..., max_length=100)
    title: str = Field(..., max_length=255)
    body: str
    channel: str = Field(..., pattern="^(push|sms|email|in_app)$")
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high|urgent)$")
    data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Notification response"""
    id: UUID
    user_id: UUID
    type: str
    title: str
    body: str
    channel: str
    priority: str
    status: str
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    clicked_at: Optional[datetime]
    data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """List of notifications"""
    notifications: List[NotificationResponse]
    total: int
    unread_count: int


# Send notification schemas
class SendPushNotification(BaseModel):
    """Send push notification"""
    user_id: UUID
    title: str = Field(..., max_length=100)
    body: str = Field(..., max_length=200)
    data: Optional[Dict[str, Any]] = None


class SendSMSNotification(BaseModel):
    """Send SMS notification"""
    user_id: UUID
    message: str = Field(..., max_length=160)


class SendEmailNotification(BaseModel):
    """Send email notification"""
    user_id: UUID
    subject: str = Field(..., max_length=200)
    body: str
    html: Optional[str] = None


class SendNotificationResponse(BaseModel):
    """Send notification response"""
    notification_id: UUID
    status: str
    message: str


# Notification preferences schemas
class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences"""
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    budget_alerts_enabled: Optional[bool] = None
    bill_reminders_enabled: Optional[bool] = None
    insights_enabled: Optional[bool] = None
    achievements_enabled: Optional[bool] = None
    marketing_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    digest_frequency: Optional[str] = Field(None, pattern="^(real_time|daily|weekly|never)$")


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response"""
    user_id: UUID
    push_enabled: bool
    sms_enabled: bool
    email_enabled: bool
    budget_alerts_enabled: bool
    bill_reminders_enabled: bool
    insights_enabled: bool
    achievements_enabled: bool
    marketing_enabled: bool
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    digest_frequency: str

    class Config:
        from_attributes = True


# Batch notification schemas
class BatchNotificationCreate(BaseModel):
    """Create batch notifications"""
    user_ids: List[UUID]
    type: str
    title: str
    body: str
    channel: str = "push"
    priority: str = "medium"
    data: Optional[Dict[str, Any]] = None


class BatchNotificationResponse(BaseModel):
    """Batch notification response"""
    total_sent: int
    total_failed: int
    notification_ids: List[UUID]
