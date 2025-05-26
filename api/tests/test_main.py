"""
Unit tests for the main FastAPI application.
"""
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from api.suggestions import SimpleMessage


@pytest.mark.asyncio
async def test_root_endpoint(test_client):
    """Test the root endpoint returns a hello message."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.asyncio
@patch('api.main.suggestion_requested')
async def test_request_endpoint(mock_suggestion_requested, test_client, mock_simple_messages):
    """Test the /api/request endpoint."""
    # Set up the mock
    mock_suggestion_requested.return_value = True
    
    # Create valid request data
    messages = [SimpleMessage(**msg) for msg in mock_simple_messages]
    request_data = [msg.model_dump() for msg in messages]
    
    # Test the endpoint
    response = test_client.post("/api/request", json=request_data)
    assert response.status_code == 200
    assert response.json() == {"requested": True}
    
    # Verify the mock was called with the correct arguments
    mock_suggestion_requested.assert_called_once()
    args = mock_suggestion_requested.call_args[0][0]
    assert len(args) == len(messages)
    for i, msg in enumerate(args):
        assert msg.name == messages[i].name
        assert msg.text == messages[i].text


@pytest.mark.asyncio
@patch('api.main.create_suggestion')
async def test_suggestion_endpoint(mock_create_suggestion, test_client, mock_simple_messages):
    """Test the /api/suggestion endpoint."""
    # Set up the mock to return a generator
    async def mock_generator():
        yield "Test "
        yield "suggestion "
        yield "response"
        
    mock_create_suggestion.return_value = mock_generator()
    
    # Create valid request data
    request_data = {
        "customer": "Test Customer",
        "messages": mock_simple_messages
    }
    
    # Test the endpoint
    response = test_client.post("/api/suggestion", json=request_data)
    assert response.status_code == 200
    # Check that content type starts with text/event-stream (ignoring charset)
    assert response.headers["content-type"].startswith("text/event-stream")
    
    # Verify the response content
    content = response.content.decode('utf-8')
    assert "Test suggestion response" == content
    
    # Verify the mock was called with the correct arguments
    mock_create_suggestion.assert_called_once_with(
        request_data["customer"], 
        [SimpleMessage(**msg) for msg in request_data["messages"]]
    )


# Removed asyncio mark since this is synchronous
def test_file_loading():
    """Test the loading of product and purchase data files.
    
    This is a simpler test that doesn't try to reload the module.
    """
    import api.main
    
    # Verify that product and purchase data was loaded
    assert len(api.main.products) > 0
    assert len(api.main.purchases) > 0
    
    # Check that prompt was loaded
    assert isinstance(api.main.prompt, str)
    assert len(api.main.prompt) > 0