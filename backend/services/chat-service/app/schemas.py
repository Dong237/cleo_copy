"""
Pydantic schemas for Chat Service
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# Message schemas
class MessageCreate(BaseModel):
    """Create message request"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None


class MessageResponse(BaseModel):
    """Message response"""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    intent: Optional[str]
    confidence: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Chat response"""
    conversation_id: UUID
    message: MessageResponse
    suggestions: Optional[List[str]] = None


class MessageFeedback(BaseModel):
    """Message feedback"""
    helpful: bool
    feedback_text: Optional[str] = None


# Conversation schemas
class ConversationResponse(BaseModel):
    """Conversation response"""
    id: UUID
    user_id: UUID
    title: Optional[str]
    personality_mode: Optional[str]
    is_active: bool
    last_message_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Conversation with messages"""
    messages: List[MessageResponse]


class ConversationListResponse(BaseModel):
    """List of conversations"""
    conversations: List[ConversationResponse]
    total: int


# Intent schemas
class IntentClassification(BaseModel):
    """Intent classification result"""
    intent: str
    confidence: float
    entities: dict = {}


# Personality responses
class PersonalityResponse(BaseModel):
    """Response with personality applied"""
    base_response: str
    personalized_response: str
    personality_mode: str
