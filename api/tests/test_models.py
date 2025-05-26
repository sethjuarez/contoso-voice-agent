"""
Unit tests for the models module.
"""
import pytest
from api.models import (
    Action, 
    Assistant, 
    Context, 
    SocketMessage, 
    ClientMessage, 
    start_assistant, 
    stream_assistant, 
    stop_assistant, 
    full_assistant, 
    send_context, 
    send_action
)


def test_action_model():
    """Test the Action model."""
    action = Action(name="test_action", arguments='{"key": "value"}')
    assert action.name == "test_action"
    assert action.arguments == '{"key": "value"}'
    
    # Test serialization
    data = action.model_dump()
    assert data["name"] == "test_action"
    assert data["arguments"] == '{"key": "value"}'


def test_assistant_model():
    """Test the Assistant model."""
    # Test with just state
    assistant = Assistant(state="start")
    assert assistant.state == "start"
    assert assistant.payload is None
    
    # Test with payload
    assistant = Assistant(state="stream", payload="test payload")
    assert assistant.state == "stream"
    assert assistant.payload == "test payload"
    
    # Test serialization
    data = assistant.model_dump()
    assert data["state"] == "stream"
    assert data["payload"] == "test payload"


def test_context_model():
    """Test the Context model."""
    context = Context(type="user", payload="test context")
    assert context.type == "user"
    assert context.payload == "test context"
    
    # Test serialization
    data = context.model_dump()
    assert data["type"] == "user"
    assert data["payload"] == "test context"


def test_socket_message_model():
    """Test the SocketMessage model with various payload types."""
    # Test with Action payload
    action = Action(name="test_action", arguments='{"key": "value"}')
    message = SocketMessage(type="action", payload=action)
    assert message.type == "action"
    assert message.payload.name == "test_action"
    
    # Test with Assistant payload
    assistant = Assistant(state="stream", payload="test payload")
    message = SocketMessage(type="assistant", payload=assistant)
    assert message.type == "assistant"
    assert message.payload.state == "stream"
    
    # Test with Context payload
    context = Context(type="user", payload="test context")
    message = SocketMessage(type="context", payload=context)
    assert message.type == "context"
    assert message.payload.type == "user"
    
    # Test serialization
    data = message.model_dump()
    assert data["type"] == "context"
    assert data["payload"]["type"] == "user"
    assert data["payload"]["payload"] == "test context"


def test_client_message_model():
    """Test the ClientMessage model."""
    # Test without image
    message = ClientMessage(name="user", text="test message")
    assert message.name == "user"
    assert message.text == "test message"
    assert message.image is None
    
    # Test with image
    message = ClientMessage(name="user", text="test with image", image="base64image")
    assert message.name == "user"
    assert message.text == "test with image"
    assert message.image == "base64image"
    
    # Test serialization
    data = message.model_dump()
    assert data["name"] == "user"
    assert data["text"] == "test with image"
    assert data["image"] == "base64image"


def test_start_assistant():
    """Test start_assistant function."""
    message_data = start_assistant()
    assert message_data["type"] == "assistant"
    assert message_data["payload"]["state"] == "start"
    assert message_data["payload"]["payload"] is None


def test_stream_assistant():
    """Test stream_assistant function."""
    chunk = "This is a test chunk"
    message_data = stream_assistant(chunk)
    assert message_data["type"] == "assistant"
    assert message_data["payload"]["state"] == "stream"
    assert message_data["payload"]["payload"] == chunk


def test_stop_assistant():
    """Test stop_assistant function."""
    message_data = stop_assistant()
    assert message_data["type"] == "assistant"
    assert message_data["payload"]["state"] == "complete"
    assert message_data["payload"]["payload"] is None


def test_full_assistant():
    """Test full_assistant function."""
    message = "This is a test message"
    message_data = full_assistant(message)
    assert message_data["type"] == "assistant"
    assert message_data["payload"]["state"] == "full"
    assert message_data["payload"]["payload"] == message


def test_send_context():
    """Test send_context function."""
    context = "This is test context"
    message_data = send_context(context)
    assert message_data["type"] == "context"
    assert message_data["payload"]["type"] == "user"
    assert message_data["payload"]["payload"] == context


def test_send_action():
    """Test send_action function."""
    name = "test_action"
    args = '{"key": "value"}'
    message_data = send_action(name, args)
    assert message_data["type"] == "action"
    assert message_data["payload"]["name"] == name
    assert message_data["payload"]["arguments"] == args