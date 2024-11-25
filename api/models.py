from pydantic import BaseModel
from typing import List, Literal, Optional

class FunctionQuery(BaseModel):
    carousel: str
    input: str


class Action(BaseModel):
    name: str
    arguments: str


class Assistant(BaseModel):
    state: Literal["start", "stream", "complete", "full"]
    payload: Optional[str] = None


class Context(BaseModel):
    type: Literal["action", "user", "issue", "article"]
    payload: str


class SocketMessage(BaseModel):
    type: Literal["action", "assistant", "context"]
    payload: Action | Assistant | Context


class ClientMessage(BaseModel):
    name: str
    image: Optional[str] = None
    text: str
    context: List[str] = []


class AgentMessage(BaseModel):
    role: str
    content: str
