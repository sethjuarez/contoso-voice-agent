"""
Utility functions for testing the API.
"""
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from unittest.mock import patch, MagicMock, AsyncMock

from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from api.suggestions import SimpleMessage


def patch_path(path_str):
    """Create a patch for a path operation."""
    return patch(path_str)


def create_mock_websocket_app():
    """Create a mock WebSocket app for testing."""
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.client_state = WebSocketState.CONNECTED
    return mock_ws


def mock_file_read(content):
    """Mock reading content from a file."""
    def mock_read_text(self):
        return content
    with patch('pathlib.Path.read_text', mock_read_text):
        yield


async def async_mock_generator(items):
    """Create an async generator from a list of items."""
    for item in items:
        yield item


def create_mock_chat_session(websocket=None):
    """Create a mock chat session for testing."""
    if websocket is None:
        websocket = create_mock_websocket_app()
    
    from api.session import ChatSession
    session = ChatSession(websocket)
    session.context = []
    return session


def create_simple_messages(messages: List[Dict[str, str]]) -> List[SimpleMessage]:
    """Convert a list of dictionaries to SimpleMessage objects."""
    return [SimpleMessage(**msg) for msg in messages]


def create_mock_json_response(data: Dict[str, Any]) -> str:
    """Create a mock JSON response."""
    return json.dumps(data)


class AsyncIterator:
    """
    Helper class to create objects that can be used in async for loops.
    """
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        value = self.items[self.index]
        self.index += 1
        return value