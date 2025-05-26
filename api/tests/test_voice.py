"""
Unit tests for the voice module.
"""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from api.voice import Message, RealtimeClient
from fastapi import WebSocket
from fastapi.websockets import WebSocketState


@pytest.fixture
def mock_message():
    """Create a sample Message."""
    return Message(type="user", payload="test message")


def test_message_model(mock_message):
    """Test the Message model."""
    assert mock_message.type == "user"
    assert mock_message.payload == "test message"
    
    # Test serialization
    data = mock_message.model_dump()
    assert data["type"] == "user"
    assert data["payload"] == "test message"


@pytest.mark.asyncio
async def test_realtime_client_initialization(mock_websocket, mock_realtime_client):
    """Test RealtimeClient initialization."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=True
    )
    
    assert client.realtime is mock_realtime_client
    assert client.client is mock_websocket
    assert client.active is True
    assert client.debug is True
    assert client.response_queue == []


@pytest.mark.asyncio
async def test_send_message(mock_websocket, mock_realtime_client, mock_message):
    """Test sending a message through the RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    await client.send_message(mock_message)
    mock_websocket.send_json.assert_called_once_with(mock_message.model_dump())


@pytest.mark.asyncio
async def test_send_audio(mock_websocket, mock_realtime_client):
    """Test sending audio through the RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    audio_message = Message(type="audio", payload="base64audio")
    await client.send_audio(audio_message)
    mock_websocket.send_json.assert_called_once_with(audio_message.model_dump())


@pytest.mark.asyncio
async def test_send_console(mock_websocket, mock_realtime_client):
    """Test sending console messages through the RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    console_message = Message(type="console", payload="test console message")
    await client.send_console(console_message)
    mock_websocket.send_json.assert_called_once_with(console_message.model_dump())


@pytest.mark.asyncio
@patch('api.voice.Session')
@patch('api.voice.SessionUpdateEvent')
async def test_update_realtime_session(
    mock_session_update_event,
    mock_session,
    mock_websocket,
    mock_realtime_client
):
    """Test updating the realtime session."""
    # Setup mocks
    mock_session.return_value = "mock_session"
    mock_session_update_event.return_value = "mock_event"
    
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    # Call method under test
    instructions = "Test instructions"
    threshold = 0.9
    silence_duration_ms = 600
    prefix_padding_ms = 400
    
    await client.update_realtime_session(
        instructions,
        threshold,
        silence_duration_ms,
        prefix_padding_ms
    )
    
    # Verify mock calls
    mock_session.assert_called_once()
    mock_session_update_event.assert_called_once_with(
        type="session.update",
        session="mock_session"
    )
    mock_realtime_client.send.assert_called_once_with("mock_event")


@pytest.mark.asyncio
async def test_closed_property(mock_websocket, mock_realtime_client):
    """Test the closed property of RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    # When client is connected
    mock_websocket.client_state = WebSocketState.CONNECTED
    assert client.closed is False
    
    # When client is disconnected
    mock_websocket.client_state = WebSocketState.DISCONNECTED
    assert client.closed is True
    
    # When client is None
    client.client = None
    assert client.closed is True


@pytest.mark.asyncio
@patch('api.voice.Message')
async def test_conversation_item_input_audio_transcription_completed(
    mock_message,
    mock_websocket,
    mock_realtime_client
):
    """Test handling of completed audio transcription."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    mock_message.return_value = Message(type="user", payload="transcribed text")
    
    # Create a mock event
    event = MagicMock()
    event.transcript = "transcribed text"
    
    # Call method
    await client._conversation_item_input_audio_transcription_completed(event)
    
    # Verify
    mock_websocket.send_json.assert_called_once()


@pytest.mark.asyncio
@patch('api.voice.Message')
async def test_response_audio_transcript_done(
    mock_message,
    mock_websocket,
    mock_realtime_client
):
    """Test handling of completed audio transcript response."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    mock_message.return_value = Message(type="assistant", payload="assistant response")
    
    # Create a mock event
    event = MagicMock()
    event.transcript = "assistant response"
    
    # Call method
    await client._response_audio_transcript_done(event)
    
    # Verify
    mock_websocket.send_json.assert_called_once()


@pytest.mark.asyncio
@patch('api.voice.Message')
async def test_response_audio_delta(
    mock_message,
    mock_websocket,
    mock_realtime_client
):
    """Test handling of audio delta response."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    mock_message.return_value = Message(type="audio", payload="audio_data")
    
    # Create a mock event
    event = MagicMock()
    event.delta = "audio_data"
    
    # Call method
    await client._response_audio_delta(event)
    
    # Verify
    mock_websocket.send_json.assert_called_once()


"""
Unit tests for the voice module.
"""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from api.voice import Message, RealtimeClient
from fastapi import WebSocket
from fastapi.websockets import WebSocketState


@pytest.fixture
def mock_message():
    """Create a sample Message."""
    return Message(type="user", payload="test message")


def test_message_model(mock_message):
    """Test the Message model."""
    assert mock_message.type == "user"
    assert mock_message.payload == "test message"
    
    # Test serialization
    data = mock_message.model_dump()
    assert data["type"] == "user"
    assert data["payload"] == "test message"


@pytest.mark.asyncio
async def test_realtime_client_initialization(mock_websocket, mock_realtime_client):
    """Test RealtimeClient initialization."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=True
    )
    
    assert client.realtime is mock_realtime_client
    assert client.client is mock_websocket
    assert client.active is True
    assert client.debug is True
    assert client.response_queue == []


@pytest.mark.asyncio
async def test_send_message(mock_websocket, mock_realtime_client, mock_message):
    """Test sending a message through the RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    await client.send_message(mock_message)
    mock_websocket.send_json.assert_called_once_with(mock_message.model_dump())


@pytest.mark.asyncio
async def test_send_audio(mock_websocket, mock_realtime_client):
    """Test sending audio through the RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    audio_message = Message(type="audio", payload="base64audio")
    await client.send_audio(audio_message)
    mock_websocket.send_json.assert_called_once_with(audio_message.model_dump())


@pytest.mark.asyncio
async def test_send_console(mock_websocket, mock_realtime_client):
    """Test sending console messages through the RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    console_message = Message(type="console", payload="test console message")
    await client.send_console(console_message)
    mock_websocket.send_json.assert_called_once_with(console_message.model_dump())


@pytest.mark.asyncio
@patch('api.voice.Session')
@patch('api.voice.SessionUpdateEvent')
async def test_update_realtime_session(
    mock_session_update_event,
    mock_session,
    mock_websocket,
    mock_realtime_client
):
    """Test updating the realtime session."""
    # Setup mocks
    mock_session.return_value = "mock_session"
    mock_session_update_event.return_value = "mock_event"
    
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    # Call method under test
    instructions = "Test instructions"
    threshold = 0.9
    silence_duration_ms = 600
    prefix_padding_ms = 400
    
    await client.update_realtime_session(
        instructions,
        threshold,
        silence_duration_ms,
        prefix_padding_ms
    )
    
    # Verify mock calls
    mock_session.assert_called_once()
    mock_session_update_event.assert_called_once_with(
        type="session.update",
        session="mock_session"
    )
    mock_realtime_client.send.assert_called_once_with("mock_event")


@pytest.mark.asyncio
async def test_closed_property(mock_websocket, mock_realtime_client):
    """Test the closed property of RealtimeClient."""
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    # When client is connected
    mock_websocket.client_state = WebSocketState.CONNECTED
    assert client.closed is False
    
    # When client is disconnected
    mock_websocket.client_state = WebSocketState.DISCONNECTED
    assert client.closed is True
    
    # When client is None
    client.client = None
    assert client.closed is True


@pytest.mark.asyncio
@patch('api.voice.Message')
async def test_conversation_item_input_audio_transcription_completed(
    mock_message,
    mock_websocket,
    mock_realtime_client
):
    """Test handling of completed audio transcription."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    mock_message.return_value = Message(type="user", payload="transcribed text")
    
    # Create a mock event
    event = MagicMock()
    event.transcript = "transcribed text"
    
    # Call method
    await client._conversation_item_input_audio_transcription_completed(event)
    
    # Verify
    mock_websocket.send_json.assert_called_once()


@pytest.mark.asyncio
@patch('api.voice.Message')
async def test_response_audio_transcript_done(
    mock_message,
    mock_websocket,
    mock_realtime_client
):
    """Test handling of completed audio transcript response."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    mock_message.return_value = Message(type="assistant", payload="assistant response")
    
    # Create a mock event
    event = MagicMock()
    event.transcript = "assistant response"
    
    # Call method
    await client._response_audio_transcript_done(event)
    
    # Verify
    mock_websocket.send_json.assert_called_once()


@pytest.mark.asyncio
@patch('api.voice.Message')
async def test_response_audio_delta(
    mock_message,
    mock_websocket,
    mock_realtime_client
):
    """Test handling of audio delta response."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    mock_message.return_value = Message(type="audio", payload="audio_data")
    
    # Create a mock event
    event = MagicMock()
    event.delta = "audio_data"
    
    # Call method
    await client._response_audio_delta(event)
    
    # Verify
    mock_websocket.send_json.assert_called_once()


@pytest.mark.asyncio
@patch('api.voice.Message')
@patch('api.voice.json.loads')
async def test_receive_client_audio(
    mock_json_loads,
    mock_message,
    mock_websocket,
    mock_realtime_client
):
    """Test receiving audio from client."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    # First call returns audio, second call raises exception to exit the loop
    mock_websocket.receive_text.side_effect = [
        json.dumps({"type": "audio", "payload": "audio_data"}),
        Exception("WebSocket disconnected")
    ]
    
    mock_message.return_value = Message(type="audio", payload="audio_data")
    mock_json_loads.return_value = {"type": "audio", "payload": "audio_data"}
    
    # Call method and catch expected exception
    try:
        await client.receive_client()
    except Exception:
        pass
    
    # Verify receive_text was called (at least once)
    assert mock_websocket.receive_text.call_count >= 1
    mock_realtime_client.send.assert_called()


@pytest.mark.asyncio
async def test_close(mock_websocket, mock_realtime_client):
    """Test closing the RealtimeClient."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    # Call method
    await client.close()
    
    # Verify
    mock_websocket.close.assert_called_once()
    mock_realtime_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_close(mock_websocket, mock_realtime_client):
    """Test closing the RealtimeClient."""
    # Setup
    client = RealtimeClient(
        realtime=mock_realtime_client,
        client=mock_websocket,
        debug=False
    )
    
    # Call method
    await client.close()
    
    # Verify
    mock_websocket.close.assert_called_once()
    mock_realtime_client.close.assert_called_once()