"""
Unit tests for the writeup functionality.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

import json
from api.suggestions import SimpleMessage, suggestion_requested


@pytest.mark.asyncio
@patch('prompty.execute_async')
async def test_writeup_positive_response(mock_execute_async):
    """Test writeup functionality with a positive response."""
    # Setup
    async def mock_async_return():
        return "Yes, I think the customer would benefit from product suggestions."
    
    mock_execute_async.return_value = mock_async_return()
    
    messages = [
        SimpleMessage(name="user", text="I need help finding gear for my trip"),
        SimpleMessage(name="assistant", text="What kind of trip are you planning?"),
        SimpleMessage(name="user", text="Winter camping in the mountains")
    ]
    
    # Execute
    result = await suggestion_requested(messages)
    
    # Verify
    assert result is True
    mock_execute_async.assert_called_once()


@pytest.mark.asyncio
@patch('prompty.execute_async')
async def test_writeup_negative_response(mock_execute_async):
    """Test writeup functionality with a negative response."""
    # Setup
    async def mock_async_return():
        return "No, the customer is not asking about products."
    
    mock_execute_async.return_value = mock_async_return()
    
    messages = [
        SimpleMessage(name="user", text="How do I return something?"),
        SimpleMessage(name="assistant", text="I can help with that. What item do you want to return?")
    ]
    
    # Execute
    result = await suggestion_requested(messages)
    
    # Verify
    assert result is False
    mock_execute_async.assert_called_once()


@pytest.mark.asyncio
@patch('prompty.execute_async')
async def test_writeup_with_various_responses(mock_execute_async):
    """Test writeup handling of various affirmative and negative responses."""
    test_cases = [
        # Affirmative responses
        ("YES", True),
        ("Yes, definitely", True),
        ("y", True),
        ("yeah", True),
        # Negative responses
        ("NO", False),
        ("No, not needed", False),
        ("n", False),
        ("nope", False),
        # Responses with explanation
        ("Yes, the customer is asking about winter gear", True),
        ("No, the conversation is about returns policy", False)
    ]
    
    for response, expected in test_cases:
        # Setup
        async def mock_async_return():
            return response
        
        mock_execute_async.return_value = mock_async_return()
        
        messages = [SimpleMessage(name="user", text="Test prompt")]
        
        # Execute
        result = await suggestion_requested(messages)
        
        # Verify
        assert result is expected
        mock_execute_async.assert_called()
        mock_execute_async.reset_mock()
