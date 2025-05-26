"""
Module to patch various dependencies for testing.
"""
import sys
import asyncio
from unittest.mock import MagicMock, patch

class AsyncMockWrapper:
    """Wrapper for mocking async functions that can return either awaitable or non-awaitable values."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        
    async def __call__(self, *args, **kwargs):
        if asyncio.iscoroutine(self.return_value) or asyncio.isfuture(self.return_value) or hasattr(self.return_value, '__aiter__'):
            return await self.return_value
        return self.return_value


# Mock prompty.load to avoid loading actual prompty files
def mock_prompty_load_patch():
    mock_prompty = MagicMock()
    return patch('prompty.load', return_value=mock_prompty)


# Mock the entire prompty module
def mock_prompty_module():
    mock_module = MagicMock()
    
    # Mock load function
    mock_module.load.return_value = MagicMock()
    
    # Create async mock for execute_async
    async def async_execute(*args, **kwargs):
        return '{"response": "This is a test response", "context": "Test context", "call": 0.8}'
    
    mock_module.execute_async = AsyncMockWrapper(async_execute())
    
    # Setup module mocks
    sys.modules['prompty'] = mock_module
    sys.modules['prompty.azure'] = MagicMock()
    
    # Create a trace function that handles arguments correctly
    def trace_function(*args, **kwargs):
        if args and callable(args[0]):
            # Called as @trace
            return args[0]
        # Called as @trace(name="something")
        return lambda f: f
        
    tracer_mock = MagicMock()
    tracer_mock.trace = trace_function
    tracer_mock.SIGNATURE = "signature"
    tracer_mock.INPUTS = "inputs"
    tracer_mock.RESULT = "result"
    
    # Mock tracer start context manager
    mock_context = MagicMock()
    mock_context.__enter__ = MagicMock(return_value=MagicMock())
    mock_context.__exit__ = MagicMock(return_value=None)
    tracer_mock.start.return_value = mock_context
    
    sys.modules['prompty.tracer'] = MagicMock()
    sys.modules['prompty.tracer'].trace = trace_function
    sys.modules['prompty.tracer'].Tracer = tracer_mock
    
    return mock_module