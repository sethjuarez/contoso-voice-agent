"""Mock data for testing."""

from typing import Dict, Any, List, AsyncGenerator
from pathlib import Path

MOCK_CHAT_RESPONSE = {
    "response": "Test response",
    "context": "Test context",
    "call": 0.8
}

MOCK_SUGGESTION_TEMPLATE = {
    "type": "suggestion",
    "message": "Here's a relevant product for your camping trip: TrekReady Hiking Boots",
    "formatted": "I notice you're planning a camping trip. You might be interested in the TrekReady Hiking Boots. They're perfect for hiking and provide excellent traction and support."
}

async def mock_create_suggestion(customer: str, messages: List[Any]) -> AsyncGenerator[str, None]:
    """Mock suggestion generator for testing."""
    mock_response = {
        "type": "suggestion",
        "message": "Test suggestion",
        "formatted": "Here's a test suggestion for you!"
    }
    yield f"data: {mock_response}"

async def mock_suggestion_requested(messages: List[Any]) -> bool:
    """Mock suggestion request checker for testing."""
    for msg in messages:
        if "camping" in msg.content.lower():
            return True
    return False