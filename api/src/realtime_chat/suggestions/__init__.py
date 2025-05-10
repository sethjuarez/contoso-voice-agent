"""Product suggestion module."""

from typing import List
from pydantic import BaseModel
from ..core.mockdata import mock_create_suggestion, mock_suggestion_requested

class SimpleMessage(BaseModel):
    name: str
    text: str

# For testing, use mock functions
create_suggestion = mock_create_suggestion
suggestion_requested = mock_suggestion_requested
