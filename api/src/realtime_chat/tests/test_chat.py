"""Tests for chat functionality."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from realtime_chat.handlers.api import app
from realtime_chat.core.session import Message, ChatSession, SessionManager

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def chat_message():
    return {
        "name": "Test User",
        "text": "Hello!",
        "threadId": "test-thread",
        "image": None
    }

@pytest.fixture
def voice_settings():
    return {
        "user": "Test User",
        "threshold": 0.8,
        "silence": 500,
        "prefix": 300
    }

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_websocket_chat_connection(client):
    with client.websocket_connect("/api/chat") as websocket:
        websocket.send_json({"threadId": "test-123"})
        # Should be able to connect without errors

@pytest.mark.asyncio
async def test_session_creation():
    thread_id = "test-thread"
    websocket = AsyncMock()
    
    # Clear any existing sessions
    SessionManager.sessions = {}
    
    session = await SessionManager.create_session(thread_id, websocket)
    assert isinstance(session, ChatSession)
    assert thread_id in SessionManager.sessions
    assert session.client == websocket

@pytest.mark.asyncio
async def test_session_cleanup():
    thread_id = "test-thread"
    websocket = AsyncMock()
    
    # Create a session
    session = await SessionManager.create_session(thread_id, websocket)
    assert thread_id in SessionManager.sessions
    
    # Clear sessions
    await SessionManager.clear_sessions()
    assert thread_id not in SessionManager.sessions

@pytest.mark.asyncio
async def test_chat_message_flow():
    thread_id = "test-thread"
    websocket = AsyncMock()
    test_message = {"name": "Test User", "text": "Hello", "image": None}
    test_response = {
        "response": "Hi there!",
        "context": "Greeting context",
        "call": 0.5
    }
    
    # Create session
    session = await SessionManager.create_session(thread_id, websocket)
    
    # Mock receive_json to return test message then simulate disconnect
    websocket.receive_json.side_effect = [test_message]
    websocket.client_state = "DISCONNECTED"
    
    # Mock create_response to return test response
    with patch("realtime_chat.chat.create_response") as mock_create:
        mock_create.return_value = test_response
        await session.receive_chat()
    
    # Verify message flow
    expected_calls = [
        # Start assistant
        {"role": "assistant", "text": "", "start": "true"},
        # Stream response
        {"role": "assistant", "text": "Hi there!"},
        # Stop assistant
        {"role": "assistant", "text": "", "stop": "true"},
        # Send context
        {"role": "context", "text": "Greeting context"},
    ]
    
    assert len(websocket.send_json.mock_calls) >= len(expected_calls)
    
    # Verify context was stored
    assert len(session.context) == 1
    assert session.context[0] == test_response["context"]