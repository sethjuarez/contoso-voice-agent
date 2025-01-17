from pydantic import BaseModel
from typing import Literal, Optional


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


def start_assistant():
    return SocketMessage(
        type="assistant", payload=Assistant(state="start")
    ).model_dump()


def stream_assistant(chunk: str):
    return SocketMessage(
        type="assistant", payload=Assistant(state="stream", payload=chunk)
    ).model_dump()


def stop_assistant():
    return SocketMessage(
        type="assistant", payload=Assistant(state="complete")
    ).model_dump()


def full_assistant(message: str):
    return SocketMessage(
        type="assistant", payload=Assistant(state="full", payload=message)
    ).model_dump()


def send_context(context: str):
    return SocketMessage(
        type="context", payload=Context(type="user", payload=context)
    ).model_dump()

def send_action(name: str, arguments: str):
    return SocketMessage(
        type="action", payload=Action(name=name, arguments=arguments)
    ).model_dump()