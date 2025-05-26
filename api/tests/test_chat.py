
"""
Unit tests for the chat module functionality.
"""
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from api.chat import create_response


@pytest.mark.asyncio
@patch('prompty.execute_async')
async def test_create_response_basic(mock_execute_async):
    """Test basic functionality of create_response."""
    # Setup mock response
    mock_response = {
        "response": "Here's information about tents.",
        "context": "User asked about tents",
        "call": 0.2
    }
    
    # Make the mock return an awaitable that returns the JSON string
    async def mock_async_return():
        return json.dumps(mock_response)
    
    mock_execute_async.return_value = mock_async_return()
    
    # Call the function
    customer = "Test Customer"
    question = "Tell me about tents"
    context = []
    
    result = await create_response(customer, question, context)
    
    # Verify results
    assert result == mock_response
    mock_execute_async.assert_called_once()
    _, kwargs = mock_execute_async.call_args
    assert kwargs['inputs']['customer'] == customer
    assert kwargs['inputs']['question'] == question
    assert kwargs['inputs']['context'] == []


@pytest.mark.asyncio
@patch('prompty.execute_async')
async def test_create_response_with_context(mock_execute_async):
    """Test create_response with context."""
    # Setup mock response
    mock_response = {
        "response": "Based on your previous interest in tents, here's information about sleeping bags.",
        "context": "User asked about sleeping bags after tents",
        "call": 0.1
    }
    
    # Make the mock return an awaitable that returns the JSON string
    async def mock_async_return():
        return json.dumps(mock_response)
    
    mock_execute_async.return_value = mock_async_return()
    
    # Call the function
    customer = "Test Customer"
    question = "What about sleeping bags?"
    context = ["User previously asked about tents"]
    
    result = await create_response(customer, question, context)
    
    # Verify results
    assert result == mock_response
    mock_execute_async.assert_called_once()
    _, kwargs = mock_execute_async.call_args
    assert kwargs['inputs']['context'] == context


@pytest.mark.asyncio
@patch('prompty.execute_async')
async def test_create_response_with_image(mock_execute_async):
    """Test create_response with an image."""
    # Setup mock response
    mock_response = {
        "response": "This tent in the image looks like our SkyView 2-Person Tent.",
        "context": "User sent an image of a tent",
        "call": 0.5
    }
    
    # Make the mock return an awaitable that returns the JSON string
    async def mock_async_return():
        return json.dumps(mock_response)
    
    mock_execute_async.return_value = mock_async_return()
    
    # Call the function
    customer = "Test Customer"
    question = "What tent is this?"
    context = []
    image = "base64encodedimage"
    
    result = await create_response(customer, question, context, image)
    
    # Verify results
    assert result == mock_response
    mock_execute_async.assert_called_once()
    _, kwargs = mock_execute_async.call_args
    assert 'image' in kwargs['inputs']
    assert kwargs['inputs']['image'] == image


def test_groundedness():
    """
    Test if the response is grounded in the product information.
    
    This would typically use the GroundednessEvaluator to check if the response
    contains accurate information about products in the catalog.
    """
    # For now, we'll use a mock implementation
    response = "The SkyView 2-Person Tent has weather resistance features and is easy to set up."
    product = {
        "name": "SkyView 2-Person Tent",
        "features": ["weather resistance", "easy setup"]
    }
    
    # Simple check: does response contain product features (in any form)?
    response_lower = response.lower()
    assert "weather resistance" in response_lower or "weather-resistance" in response_lower
    assert "easy" in response_lower and "set up" in response_lower


def test_relevance():
    """
    Test if the response is relevant to the user query.
    
    This would typically use the RelevanceEvaluator to ensure the response
    addresses the specific question or topic raised by the user.
    """
    # For now, we'll use a mock implementation
    query = "Can you recommend a sleeping bag for cold weather?"
    response = "For cold weather, I recommend the MountainDream Sleeping Bag, rated for temperatures as low as 15°F."
    
    # Simple check: does response mention the category asked about?
    assert "sleeping bag" in query.lower()
    assert "sleeping bag" in response.lower()
    assert "cold weather" in query.lower()
    assert any(temp_indicator in response.lower() for temp_indicator in ["cold", "15", "temperature"])


def test_coherence():
    """
    Test if the response maintains a coherent flow with previous context.
    
    This would typically use the CoherenceEvaluator to check if the response
    makes sense in the context of the previous conversation.
    """
    # For now, we'll use a mock implementation
    context = [
        {"role": "user", "content": "I'm going camping in Alaska next month."},
        {"role": "assistant", "content": "Great! Alaska can be quite cold, even in summer. What gear do you need help with?"},
        {"role": "user", "content": "I need a sleeping bag."}
    ]
    response = "For Alaska's cold climate, I recommend our MountainDream Sleeping Bag which is rated for temperatures down to 15°F."
    
    # Simple check: does response acknowledge the location mentioned in context?
    assert "alaska" in context[0]["content"].lower()
    assert any(cold_term in response.lower() for cold_term in ["cold", "15", "temperature"])


def test_fluency():
    """
    Test if the response is grammatically correct and reads naturally.
    
    This would typically use the FluencyEvaluator to check the linguistic
    quality of the generated text.
    """
    # For now, we'll use a mock implementation
    response = "The SkyView 2-Person Tent is our bestseller. It features weather resistance and easy setup. Many customers love it for weekend camping trips."
    
    # Simple checks for basic grammar issues
    sentences = response.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Each sentence should start with a capital letter
    for sentence in sentences:
        if sentence:
            assert sentence[0].isupper()
    
    # No repeated words (simple check)
    words = response.lower().split()
    for i in range(len(words) - 1):
        assert words[i] != words[i + 1]