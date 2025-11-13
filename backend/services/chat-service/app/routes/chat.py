"""
Chat interaction routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../.."))

from shared.database import get_db
from shared.auth import get_current_user
from shared.exceptions import ValidationException

from app.schemas import MessageCreate, ChatResponse, MessageResponse, MessageFeedback
from app.models import Conversation, Message
from app.ai.intent_classifier import IntentClassifier
from app.ai.response_generator import ResponseGenerator

router = APIRouter()


async def get_user_personality(user_id: str, db: AsyncSession) -> str:
    """
    Get user's preferred personality mode
    In production, this would query the user service
    """
    # Mock - return supportive as default
    return "supportive"


async def get_financial_data(intent: str, entities: dict, user_id: str, db: AsyncSession) -> str:
    """
    Fetch relevant financial data based on intent
    In production, this would call other microservices
    """
    # Mock responses for different intents
    if intent == "spending_query":
        if "month" in str(entities):
            return "You spent $1,245.50 this month"
        return "You spent $45.50 today"

    elif intent == "balance_query":
        return "$2,750.00"

    elif intent == "budget_query":
        return "You're at 75% of your monthly budget with 10 days left"

    elif intent == "savings_query":
        return "You've saved $1,200 towards your $5,000 emergency fund goal (24% complete)"

    elif intent == "bill_query":
        return "You have 3 bills due this week: Netflix ($15.99), Internet ($80), Electric ($120)"

    return None


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message and get AI response
    """
    start_time = time.time()

    # Get or create conversation
    if message_data.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == message_data.conversation_id,
                Conversation.user_id == current_user["user_id"]
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise ValidationException("Conversation not found")
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=current_user["user_id"],
            is_active=True
        )
        db.add(conversation)
        await db.flush()

    # Classify intent
    intent, confidence = IntentClassifier.classify(message_data.message)
    entities = IntentClassifier.extract_entities(message_data.message, intent)

    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=current_user["user_id"],
        role="user",
        content=message_data.message,
        intent=intent,
        confidence=confidence,
        created_at=datetime.utcnow()
    )
    db.add(user_message)

    # Get user's personality mode
    personality = await get_user_personality(current_user["user_id"], db)

    # Fetch relevant financial data
    financial_data = await get_financial_data(intent, entities, current_user["user_id"], db)

    # Generate response
    response_content = ResponseGenerator.generate(intent, personality, financial_data)
    suggestions = ResponseGenerator.generate_suggestions(intent)

    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)

    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=current_user["user_id"],
        role="assistant",
        content=response_content,
        intent=intent,
        confidence=confidence,
        response_time_ms=response_time_ms,
        created_at=datetime.utcnow()
    )
    db.add(assistant_message)

    # Update conversation
    conversation.last_message_at = datetime.utcnow()

    # Generate title if this is the first message
    if not conversation.title:
        conversation.title = message_data.message[:50] + ("..." if len(message_data.message) > 50 else "")

    await db.commit()
    await db.refresh(assistant_message)

    return ChatResponse(
        conversation_id=conversation.id,
        message=MessageResponse(
            id=assistant_message.id,
            conversation_id=assistant_message.conversation_id,
            role=assistant_message.role,
            content=assistant_message.content,
            intent=assistant_message.intent,
            confidence=assistant_message.confidence,
            created_at=assistant_message.created_at
        ),
        suggestions=suggestions
    )


@router.post("/message/{message_id}/feedback")
async def submit_feedback(
    message_id: str,
    feedback: MessageFeedback,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit feedback on a message
    """
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.user_id == current_user["user_id"]
        )
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.helpful = feedback.helpful
    message.feedback_text = feedback.feedback_text

    await db.commit()

    return {"message": "Feedback submitted successfully"}


@router.post("/quick-action/{action}")
async def quick_action(
    action: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute quick actions (common queries)
    """
    quick_actions_map = {
        "balance": "What's my balance?",
        "spending_today": "How much did I spend today?",
        "spending_month": "How much did I spend this month?",
        "budget_status": "How's my budget looking?",
        "upcoming_bills": "What bills are coming up?",
        "savings_progress": "How are my savings goals doing?"
    }

    message_text = quick_actions_map.get(action)

    if not message_text:
        raise ValidationException(f"Unknown quick action: {action}")

    # Process as regular message
    message_data = MessageCreate(message=message_text)
    return await send_message(message_data, current_user, db)
