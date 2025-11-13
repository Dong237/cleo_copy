"""
Conversation management routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import NotFoundException

from app.schemas import (
    ConversationResponse,
    ConversationWithMessages,
    ConversationListResponse,
    MessageResponse
)
from app.models import Conversation, Message

router = APIRouter()


@router.get("", response_model=ConversationListResponse)
async def get_conversations(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all conversations for current user
    """
    result = await db.execute(
        select(Conversation).where(
            Conversation.user_id == current_user["user_id"]
        ).order_by(desc(Conversation.last_message_at)).limit(limit)
    )
    conversations = result.scalars().all()

    return ConversationListResponse(
        conversations=conversations,
        total=len(conversations)
    )


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation with all messages
    """
    # Get conversation
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user["user_id"]
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundException("Conversation not found")

    # Get messages
    messages_result = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()

    return ConversationWithMessages(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        personality_mode=conversation.personality_mode,
        is_active=conversation.is_active,
        last_message_at=conversation.last_message_at,
        created_at=conversation.created_at,
        messages=[
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                intent=msg.intent,
                confidence=msg.confidence,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (archive) a conversation
    """
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user["user_id"]
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundException("Conversation not found")

    conversation.is_active = False
    await db.commit()

    return {"message": "Conversation deleted successfully"}


@router.post("/{conversation_id}/clear")
async def clear_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear all messages in a conversation
    """
    # Verify conversation exists and belongs to user
    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user["user_id"]
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise NotFoundException("Conversation not found")

    # Delete all messages
    await db.execute(
        Message.__table__.delete().where(
            Message.conversation_id == conversation_id
        )
    )

    await db.commit()

    return {"message": "Conversation cleared successfully"}
