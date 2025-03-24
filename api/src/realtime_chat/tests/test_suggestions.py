"""Tests for suggestions functionality."""

import json
import pytest
from fastapi.testclient import TestClient

from realtime_chat.handlers.api import app
from realtime_chat.suggestions import SimpleMessage, create_suggestion, suggestion_requested

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def messages():
    return [
        SimpleMessage(role="user", content="Hi there!"),
        SimpleMessage(role="assistant", content="Hello! How can I help you?"),
        SimpleMessage(role="user", content="I need help choosing camping gear"),
    ]

@pytest.fixture
def suggestion_request():
    return {
        "customer": "Test User",
        "messages": [
            {"role": "user", "content": "I need camping gear"},
            {"role": "assistant", "content": "I can help with that! What kind of camping are you planning?"},
        ]
    }

@pytest.mark.asyncio
async def test_suggestion_requested_with_camping_keywords():
    messages = [
        SimpleMessage(role="user", content="I need help with camping gear"),
        SimpleMessage(role="assistant", content="I can help you find the right equipment")
    ]
    
    result = await suggestion_requested(messages)
    assert result == True

@pytest.mark.asyncio
async def test_suggestion_requested_without_relevant_keywords():
    messages = [
        SimpleMessage(role="user", content="How's the weather today?"),
        SimpleMessage(role="assistant", content="It's sunny!")
    ]
    
    result = await suggestion_requested(messages)
    assert result == False

def test_suggestions_endpoint(client, suggestion_request):
    response = client.post("/api/suggestion", json=suggestion_request)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

def test_request_endpoint(client, messages):
    response = client.post(
        "/api/request",
        json=[msg.model_dump() for msg in messages]
    )
    assert response.status_code == 200
    assert "requested" in response.json()
    assert isinstance(response.json()["requested"], bool)

@pytest.mark.asyncio
async def test_create_suggestion_stream():
    customer = "Test User"
    messages = [
        SimpleMessage(role="user", content="I need camping gear")
    ]
    
    # Create async generator from create_suggestion
    generator = create_suggestion(customer, messages)
    
    # Collect first response
    first_response = await generator.__anext__()
    
    # Verify response format
    assert isinstance(first_response, str)
    # Response should be SSE format: data: {...}\n\n
    assert first_response.startswith("data: ")
    assert first_response.endswith("\n\n")
    
    # Parse JSON from response
    data = json.loads(first_response[6:-2])  # Remove "data: " and "\n\n"
    assert "message" in data  # Basic validation of suggestion structure