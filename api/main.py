import os
import asyncio
from pathlib import Path
from rtclient import RTLowLevelClient
from api.realtime import RealtimeVoiceClient
from api.session import RealtimeSession, SessionManager
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

AZURE_VOICE_ENDPOINT = os.getenv("AZURE_VOICE_ENDPOINT")
AZURE_VOICE_KEY = os.getenv("AZURE_VOICE_KEY")

prompt = (Path(__file__).parent / "prompt.txt").read_text()

app = FastAPI()


origins = [
    "*",  # Allow all origins
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # manage lifetime scope
        pass
        yield
    finally:
        # remove all stray sockets
        pass


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


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

        await session.start_chat()

    except WebSocketDisconnect as e:
        print("Chat Socket Disconnected", e)


@app.websocket("/api/voice")
async def voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        async with RTLowLevelClient(
            url=AZURE_VOICE_ENDPOINT,
            key_credential=AzureKeyCredential(AZURE_VOICE_KEY),
            azure_deployment="gpt-4o-realtime-preview",
        ) as rt:
            session = RealtimeSession(RealtimeVoiceClient(rt, verbose=True), websocket)
            await session.send_realtime_instructions(prompt)
            tasks = [
                asyncio.create_task(session.receive_realtime()),
                asyncio.create_task(session.receive_client()),
            ]
            await asyncio.gather(*tasks)

    except WebSocketDisconnect as e:
        print("Voice Socket Disconnected", e)
