import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket, WebSocketState

from realtime_chat.session import ChatSession, SessionManager, Message, ClientMessage

@pytest.fixture
def websocket_mock():
    ws = AsyncMock(spec=WebSocket)
    ws.client_state = WebSocketState.CONNECTED
    return ws

@pytest.fixture
def session(websocket_mock):
    return ChatSession(websocket_mock)

@pytest.fixture
def message():
    return Message(
        role="user",
        name="test_user",
        threadId="test_thread",
        text="Hello",
        payload="test_payload"
    )

@pytest.mark.asyncio
async def test_session_send_message(session, message):
    await session.send_message(message)
    session.client.send_json.assert_called_once_with(message.model_dump())

@pytest.mark.asyncio
async def test_session_is_closed_with_disconnected_client(session):
    session.client.client_state = WebSocketState.DISCONNECTED
    assert session.is_closed()

def test_session_manager_create_and_get():
    thread_id = "test_thread"
    websocket_mock = AsyncMock(spec=WebSocket)
    
    # Clear any existing sessions
    SessionManager.sessions = {}
    
    # Create session
    session = SessionManager.get_session(thread_id)
    assert session is None
    
    # Add session
    SessionManager.sessions[thread_id] = ChatSession(websocket_mock)
    
    # Get session
    session = SessionManager.get_session(thread_id)
    assert session is not None
    assert isinstance(session, ChatSession)

@pytest.mark.asyncio
async def test_session_receive_chat(session):
    received_message = {
        "name": "test_user",
        "text": "Hello",
        "image": None,
    }
    context_response = {
        "response": "Hello back!",
        "context": "Test context",
        "call": 0.8
    }
    
    # Mock receive_json to first return our test message then raise WebSocketDisconnect
    session.client.receive_json.side_effect = [received_message]
    session.client.client_state = WebSocketState.DISCONNECTED
    
    with patch("realtime_chat.session.create_response") as mock_create_response:
        mock_create_response.return_value = context_response
        await session.receive_chat()

    # Verify messages were sent in correct order
    assert len(session.client.send_json.mock_calls) == 4
    
    # Check context was saved
    assert session.context == [context_response["context"]]