"""
Tests for Chat Service
"""
import pytest
from httpx import AsyncClient

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from services.chat_service.main import app
from services.chat_service.app.ai.intent_classifier import IntentClassifier
from services.chat_service.app.ai.response_generator import ResponseGenerator


@pytest.fixture
async def authenticated_client():
    """Create authenticated client"""
    return {"Authorization": "Bearer mock-token-for-testing"}


# Test Intent Classifier
def test_intent_classification_spending():
    """Test spending query intent classification"""
    message = "How much did I spend on food this month?"
    intent, confidence = IntentClassifier.classify(message)

    assert intent == "spending_query"
    assert confidence > 0.5


def test_intent_classification_balance():
    """Test balance query intent classification"""
    message = "What's my balance?"
    intent, confidence = IntentClassifier.classify(message)

    assert intent == "balance_query"
    assert confidence > 0.5


def test_intent_classification_greeting():
    """Test greeting intent classification"""
    message = "Hello"
    intent, confidence = IntentClassifier.classify(message)

    assert intent == "greeting"
    assert confidence > 0.5


def test_entity_extraction():
    """Test entity extraction from message"""
    message = "How much did I spend on food last month?"
    entities = IntentClassifier.extract_entities(message, "spending_query")

    assert "category" in entities
    assert "period" in entities
    assert entities["period"] == "last_month"


# Test Response Generator
def test_response_generation_supportive():
    """Test supportive personality response"""
    response = ResponseGenerator.generate("greeting", "supportive")

    assert len(response) > 0
    assert isinstance(response, str)


def test_response_generation_funny():
    """Test funny personality response"""
    response = ResponseGenerator.generate("greeting", "funny")

    assert len(response) > 0
    # Funny responses often contain emojis or exclamation marks
    assert any(char in response for char in ["!", "?", "😄", "👋"])


def test_response_generation_roast():
    """Test roast mode personality response"""
    response = ResponseGenerator.generate("greeting", "roast")

    assert len(response) > 0


def test_suggestions_generation():
    """Test generating follow-up suggestions"""
    suggestions = ResponseGenerator.generate_suggestions("spending_query")

    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(isinstance(s, str) for s in suggestions)


# Test API Endpoints
@pytest.mark.asyncio
async def test_send_message(authenticated_client):
    """Test sending a chat message"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        message_data = {
            "message": "How much did I spend this month?"
        }
        response = await client.post(
            "/api/v1/chat/message",
            json=message_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "message" in data
        assert data["message"]["role"] == "assistant"
        assert len(data["message"]["content"]) > 0


@pytest.mark.asyncio
async def test_send_message_with_conversation_id(authenticated_client):
    """Test sending message in existing conversation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First message
        first_message = {"message": "Hello"}
        first_response = await client.post(
            "/api/v1/chat/message",
            json=first_message,
            headers=authenticated_client
        )

        conversation_id = first_response.json()["conversation_id"]

        # Follow-up message
        second_message = {
            "message": "What's my balance?",
            "conversation_id": conversation_id
        }
        response = await client.post(
            "/api/v1/chat/message",
            json=second_message,
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id


@pytest.mark.asyncio
async def test_quick_action(authenticated_client):
    """Test quick action"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat/quick-action/balance",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "message" in data


@pytest.mark.asyncio
async def test_get_conversations(authenticated_client):
    """Test getting conversation list"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/conversations",
            headers=authenticated_client
        )

        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_submit_message_feedback(authenticated_client):
    """Test submitting feedback on a message"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First, send a message
        message_data = {"message": "Test message"}
        message_response = await client.post(
            "/api/v1/chat/message",
            json=message_data,
            headers=authenticated_client
        )

        message_id = message_response.json()["message"]["id"]

        # Submit feedback
        feedback_data = {
            "helpful": True,
            "feedback_text": "Great response!"
        }
        response = await client.post(
            f"/api/v1/chat/message/{message_id}/feedback",
            json=feedback_data,
            headers=authenticated_client
        )

        assert response.status_code == 200
