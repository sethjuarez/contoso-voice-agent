"""
Voice + Text Configurator API

This module implements a FastAPI server that provides both RESTful and WebSocket endpoints
for real-time voice and text communication. The server integrates with Azure Voice Services
for speech-to-text and text-to-speech capabilities.

Key components:
- REST endpoints for suggestions and requests
- WebSocket endpoints for chat and voice communication
- Session management for persistent connections
- Integration with Azure Voice Services
- Telemetry and tracing support
"""

import json
import os
import asyncio
from pathlib import Path
from typing import List
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader

from pydantic import BaseModel
from rtclient import RTLowLevelClient  # type: ignore
from api.realtime import RealtimeVoiceClient
from api.session import Message, RealtimeSession, SessionManager
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.suggestions import SimpleMessage, create_suggestion, suggestion_requested
from dotenv import load_dotenv
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api.telemetry import init_tracing

load_dotenv()

AZURE_VOICE_ENDPOINT = os.getenv("AZURE_VOICE_ENDPOINT")
AZURE_VOICE_KEY = os.getenv("AZURE_VOICE_KEY", "fake_key")

LOCAL_TRACING_ENABLED = os.getenv("LOCAL_TRACING_ENABLED", "true") == "true"
init_tracing(local_tracing=LOCAL_TRACING_ENABLED)

base_path = Path(__file__).parent

# Load products and purchases
# NOTE: This would generally be accomplished by querying a database
products = json.loads((base_path / "products.json").read_text())
purchases = json.loads((base_path / "purchases.json").read_text())

# jinja2 template environment
env = Environment(loader=FileSystemLoader(base_path / "call"))

prompt = (Path(__file__).parent / "prompt.txt").read_text()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # manage lifetime scope
        yield
    finally:
        # remove all stray sockets
        SessionManager.clear_sessions()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Hello World"}


class SuggestionPostRequest(BaseModel):
    """
    Request model for the suggestion endpoint.
    
    Attributes:
        customer: Customer identifier
        messages: List of previous chat messages for context
    """
    customer: str
    messages: List[SimpleMessage]


@app.post("/api/suggestion")
async def suggestion(suggestion: SuggestionPostRequest):
    """
    Generate AI suggestions based on chat history.
    
    Returns a streaming response containing AI-generated suggestions
    based on the customer context and previous messages.
    """
    return StreamingResponse(
        create_suggestion(suggestion.customer, suggestion.messages),
        media_type="text/event-stream",
    )


@app.post("/api/request")
async def request(messages: List[SimpleMessage]):
    """
    Check if a suggestion should be requested based on message context.
    
    Returns:
        dict: Contains 'requested' boolean indicating if a suggestion is needed
    """
    requested = await suggestion_requested(messages)
    return {
        "requested": requested,
    }


@app.websocket("/api/chat")
async def chat_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for text chat communication.
    
    Handles:
    - Session creation/retrieval based on thread ID
    - Persistent WebSocket connections
    - Message routing within sessions
    """
    await websocket.accept()
    try:
        # first message should be thread id
        data = await websocket.receive_json()
        thread_id = data["threadId"]
        session = SessionManager.get_session(thread_id)
        if not session:
            print("Creating new session")
            session = await SessionManager.create_session(thread_id, websocket)
        else:
            print(f"Reusing existing session {thread_id}")
            session.client = websocket

        await session.receive_chat()

    except WebSocketDisconnect as e:
        print("Chat Socket Disconnected", e)


@app.websocket("/api/voice")
async def voice_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice communication.
    
    Handles:
    - Voice session initialization with Azure Voice Services
    - Real-time audio streaming
    - Voice activity detection
    - Context-aware responses based on chat history
    - Audio processing configuration (threshold, silence duration, etc.)
    
    Flow:
    1. Accept WebSocket connection
    2. Initialize Azure voice client
    3. Receive initial chat context
    4. Receive user settings
    5. Configure voice session
    6. Start concurrent tasks for:
       - Real-time audio processing
       - Client message handling
    """
    await websocket.accept()
    try:
        async with RTLowLevelClient(
            url=AZURE_VOICE_ENDPOINT,
            key_credential=AzureKeyCredential(AZURE_VOICE_KEY),
            azure_deployment="gpt-4o-realtime-preview",
        ) as rt:

            # get current messages for instructions
            chat_items = await websocket.receive_json()
            message = Message(**chat_items)

            # get current username and parameters
            user_message = await websocket.receive_json()
            user = Message(**user_message)

            settings = json.loads(user.payload)
            print(
                "Starting voice session with settings:\n",
                json.dumps(settings, indent=2),
            )

            # Configure voice system with chat context
            system_message = env.get_template("script.jinja2").render(
                customer=settings["user"] if "user" in settings else "Seth",
                purchases=purchases,
                context=json.loads(message.payload),
                products=products,
            )

            session = RealtimeSession(RealtimeVoiceClient(rt, verbose=False), websocket)
            await session.send_realtime_instructions(
                system_message,
                threshold=settings["threshold"] if "threshold" in settings else 0.8,
                silence_duration_ms=(
                    settings["silence"] if "silence" in settings else 500
                ),
                prefix_padding_ms=(settings["prefix"] if "prefix" in settings else 300),
            )
            
            # Run audio processing and client message handling concurrently
            tasks = [
                asyncio.create_task(session.receive_realtime()),
                asyncio.create_task(session.receive_client()),
            ]
            await asyncio.gather(*tasks)

    except WebSocketDisconnect as e:
        print("Voice Socket Disconnected", e)


FastAPIInstrumentor.instrument_app(app, exclude_spans=["send", "receive"])
