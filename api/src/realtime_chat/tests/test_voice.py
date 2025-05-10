"""Tests for voice chat functionality."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from realtime_chat.core.session import RealtimeSession, Message
from realtime_chat.core.voice import RealtimeVoiceClient

@pytest.fixture
def websocket_mock():
    ws = AsyncMock(spec=WebSocket)
    ws.client_state = WebSocketState.CONNECTED
    return ws

@pytest.fixture
def voice_client_mock():
    client = MagicMock(spec=RealtimeVoiceClient)
    client.closed = False
    return client

@pytest.fixture
def realtime_session(websocket_mock, voice_client_mock):
    return RealtimeSession(voice_client_mock, websocket_mock)

@pytest.mark.asyncio
async def test_send_realtime_instructions(realtime_session):
    instructions = "Test instructions"
    threshold = 0.8
    silence_duration = 500
    prefix_padding = 300
    
    await realtime_session.send_realtime_instructions(
        instructions,
        threshold=threshold,
        silence_duration_ms=silence_duration,
        prefix_padding_ms=prefix_padding
    )
    
    # Verify voice client method was called with correct params
    realtime_session.realtime.send_session_update.assert_called_once_with(
        instructions, threshold, silence_duration, prefix_padding
    )

@pytest.mark.asyncio
async def test_send_message(realtime_session):
    test_message = Message(type="user", payload="Hello!")
    await realtime_session.send_message(test_message)
    
    realtime_session.client.send_json.assert_called_once_with(
        test_message.model_dump()
    )

@pytest.mark.asyncio
async def test_send_audio(realtime_session):
    test_audio = Message(type="audio", payload="base64audiodata...")
    await realtime_session.send_audio(test_audio)
    
    realtime_session.client.send_json.assert_called_once_with(
        test_audio.model_dump()
    )

@pytest.mark.asyncio
async def test_send_console(realtime_session):
    test_console = Message(type="console", payload="console message")
    await realtime_session.send_console(test_console)
    
    realtime_session.client.send_json.assert_called_once_with(
        test_console.model_dump()
    )

@pytest.mark.asyncio
async def test_receive_realtime_session_created(realtime_session):
    # Mock message from realtime client
    session_message = MagicMock()
    session_message.type = "session.created"
    session_message.content = {"status": "ready"}
    
    # Create async generator for receive_message
    async def mock_receive():
        yield session_message
        realtime_session.realtime.closed = True
        
    realtime_session.realtime.receive_message = mock_receive
    
    # Run receive_realtime
    await realtime_session.receive_realtime()
    
    # Verify console message was sent
    realtime_session.client.send_json.assert_called_once_with({
        "type": "console",
        "payload": json.dumps({"status": "ready"})
    })

@pytest.mark.asyncio
async def test_receive_realtime_transcription(realtime_session):
    # Mock transcription message
    trans_message = MagicMock()
    trans_message.type = "conversation.item.input_audio_transcription.completed"
    trans_message.content = "Test transcription"
    
    async def mock_receive():
        yield trans_message
        realtime_session.realtime.closed = True
        
    realtime_session.realtime.receive_message = mock_receive
    
    # Run receive_realtime
    await realtime_session.receive_realtime()
    
    # Verify transcription was sent
    realtime_session.client.send_json.assert_called_once_with({
        "type": "user",
        "payload": "Test transcription"
    })

@pytest.mark.asyncio
async def test_close_realtime_session(realtime_session):
    await realtime_session.close()
    
    # Verify client and realtime were closed
    realtime_session.client.close.assert_called_once()
    realtime_session.realtime.close.assert_called_once()
    assert realtime_session.client is None
    assert realtime_session.realtime is None