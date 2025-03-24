"""Test configuration with fixtures and environment setup."""

import os
from pathlib import Path
import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    with patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_KEY': 'test-key',
        'AZURE_OPENAI_VERSION': '2024-02-15-preview',
        'AZURE_VOICE_ENDPOINT': 'https://test.voice.azure.com/',
        'AZURE_VOICE_KEY': 'test-voice-key',
        'LOCAL_TRACING_ENABLED': 'false'
    }), \
    patch('realtime_chat.chat.create_response') as mock_create_response:
        mock_create_response.return_value = {
            "response": "Test response",
            "context": "Test context",
            "call": 0.8
        }
        yield

@pytest.fixture
def test_data_dir():
    """Get path to test data directory."""
    return Path(__file__).parent / 'data'

@pytest.fixture(autouse=True)
def setup_test_data(test_data_dir):
    """Create test data directory with mock files."""
    test_data_dir.mkdir(exist_ok=True)
    yield
    # Cleanup not needed for read-only test data