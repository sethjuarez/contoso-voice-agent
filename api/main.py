import json
import os
import asyncio
from pathlib import Path
from typing import List
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader

from openai import AsyncAzureOpenAI
from pydantic import BaseModel

from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from api.session import SessionManager
from api.suggestions import SimpleMessage, create_suggestion, suggestion_requested
from dotenv import load_dotenv
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api.telemetry import init_tracing
from api.voice import Message, RealtimeClient

load_dotenv()

AZURE_VOICE_ENDPOINT = os.getenv("AZURE_VOICE_ENDPOINT", "fake_endpoint")
AZURE_VOICE_KEY = os.getenv("AZURE_VOICE_KEY", "fake_key")

LOCAL_TRACING_ENABLED = os.getenv("LOCAL_TRACING_ENABLED", "true") == "true"
init_tracing(local_tracing=LOCAL_TRACING_ENABLED)

base_path = Path(__file__).parent

# Load products and purchases
# NOTE: This would generally be accomplished by querying a database
products = json.loads((base_path / "products.json").read_text())
purchases = json.loads((base_path / "purchases.json").read_text())

# jinja2 template environment
env = Environment(loader=FileSystemLoader(base_path / "voice"))

prompt = (Path(__file__).parent / "prompt.txt").read_text()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # manage lifetime scope
        yield
    finally:
        # remove all stray sockets
        await SessionManager.clear_sessions()


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
    return {"message": "Hello World"}


class SuggestionPostRequest(BaseModel):
    customer: str
    messages: List[SimpleMessage]


@app.post("/api/suggestion")
async def suggestion(suggestion: SuggestionPostRequest):
    return StreamingResponse(
        create_suggestion(suggestion.customer, suggestion.messages),
        media_type="text/event-stream",
    )


@app.post("/api/request")
async def request(messages: List[SimpleMessage]):
    requested = await suggestion_requested(messages)
    return {
        "requested": requested,
    }


@app.websocket("/api/chat")
async def chat_endpoint(websocket: WebSocket):
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
    await websocket.accept()
    try:
        client = AsyncAzureOpenAI(
            azure_endpoint=AZURE_VOICE_ENDPOINT,
            api_key=AZURE_VOICE_KEY,
            api_version="2024-10-01-preview",
        )
        async with client.beta.realtime.connect(
            model="gpt-4o-realtime-preview",
        ) as realtime_client:

            chat_items = await websocket.receive_json()
            message = Message(**chat_items)

            # get current username
            # and receive any parameters
            user_message = await websocket.receive_json()
            user = Message(**user_message)

            settings = json.loads(user.payload)
            print(
                "Starting voice session with settings:\n",
                json.dumps(settings, indent=2),
            )

            # create voice system message
            # TODO: retrieve context from chat messages via thread id
            system_message = env.get_template("script.jinja2").render(
                customer=settings["user"] if "user" in settings else "Seth",
                purchases=purchases,
                context=json.loads(message.payload),
                products=products,
            )

            session = RealtimeClient(
                realtime=realtime_client,
                client=websocket,
            )

            await session.update_realtime_session(
                system_message,
                threshold=settings["threshold"] if "threshold" in settings else 0.8,
                silence_duration_ms=(
                    settings["silence"] if "silence" in settings else 500
                ),
                prefix_padding_ms=(settings["prefix"] if "prefix" in settings else 300),
            )

            tasks = [
                asyncio.create_task(session.receive_realtime()),
                asyncio.create_task(session.receive_client()),
            ]
            await asyncio.gather(*tasks)

    except WebSocketDisconnect as e:
        print("Voice Socket Disconnected", e)


FastAPIInstrumentor.instrument_app(app, exclude_spans=["send", "receive"])
