import json
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import WebSocket
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketState

# We need to patch prompty before importing app
from api.tests.patch_modules import mock_prompty_module

# Patch modules that might cause issues during import
mock_prompty = mock_prompty_module()

# Set environment variables for testing
import os
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://fake-openai-endpoint.azure.com"
os.environ["AZURE_OPENAI_API_KEY"] = "fake-key"
os.environ["AZURE_OPENAI_API_VERSION"] = "2024-05-01-preview"

# Import app after patching
from api.main import app


@pytest.fixture
def test_client():
    """Test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_products():
    """Mock product data."""
    return [
        {
            "id": 1,
            "name": "SkyView 2-Person Tent",
            "price": 249.99,
            "description": "Lightweight camping tent for 2 people, with weather resistance and easy setup.",
            "category": "Tents",
            "brand": "Contoso Outdoors"
        },
        {
            "id": 2,
            "name": "MountainDream Sleeping Bag",
            "price": 129.99, 
            "description": "Comfortable sleeping bag rated for 15°F, perfect for cold weather camping.",
            "category": "Sleeping Gear",
            "brand": "Contoso Outdoors"
        }
    ]


@pytest.fixture
def mock_purchases():
    """Mock purchase history data."""
    return {
        "Seth Juarez": [
            {
                "id": 1,
                "product": "SkyView 2-Person Tent",
                "purchased": "2023-01-15",
                "price": 249.99
            }
        ]
    }


@pytest.fixture
def mock_simple_messages():
    """Mock chat messages for testing."""
    return [
        {"name": "user", "text": "What do you recommend for cold weather camping?"},
        {"name": "assistant", "text": "For cold weather camping, I'd recommend the MountainDream Sleeping Bag."}
    ]


@pytest.fixture
def mock_prompty():
    """Mock for prompty.execute_async function."""
    with patch('prompty.execute_async') as mock:
        mock.return_value = '{"response": "This is a test response", "context": "Test context", "call": 0.8}'
        yield mock


@pytest.fixture
def mock_prompty_stream():
    """Mock for prompty.execute_async function that streams responses."""
    
    async def mock_stream(*args, **kwargs):
        yield "This is "
        yield "a test "
        yield "streamed response"
    
    with patch('prompty.execute_async') as mock:
        mock.return_value = mock_stream()
        yield mock


@pytest.fixture
def mock_websocket():
    """Mock WebSocket client for testing WebSocket endpoints."""
    mock_ws = MagicMock(spec=WebSocket)
    mock_ws.receive_json = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.receive_text = AsyncMock()
    mock_ws.send_text = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    return mock_ws


@pytest.fixture
def mock_realtime_client():
    """Mock for AsyncRealtimeConnection."""
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.send = AsyncMock()
    mock_client.response = MagicMock()
    mock_client.response.create = AsyncMock()
    
    # Make the client iterable in an async context
    async def mock_aiter():
        return
        yield  # This empty yield makes it an async generator
        
    mock_client.__aiter__ = lambda _: mock_aiter()
    return mock_client


@pytest.fixture
def mock_azure_openai_client():
    """Mock for AsyncAzureOpenAI client."""
    mock_client = MagicMock()
    mock_client.beta = MagicMock()
    mock_client.beta.realtime = MagicMock()
    mock_client.beta.realtime.connect = MagicMock(return_value=AsyncMock())
    return mock_client


# Patch file reading for products and purchases
@pytest.fixture(autouse=True)
def patch_file_reads(mock_products, mock_purchases):
    """Patch file reads to return mock data."""
    def mock_read_text(path):
        if path.name == "products.json":
            return json.dumps(mock_products)
        elif path.name == "purchases.json":
            return json.dumps(mock_purchases)
        elif path.name == "prompt.txt":
            return "test prompt"
        else:
            return "{}"
    
    with patch('pathlib.Path.read_text', side_effect=mock_read_text):
        yield