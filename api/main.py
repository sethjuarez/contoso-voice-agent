import os
import asyncio
from pathlib import Path
from typing import List
from rtclient import RTLowLevelClient
from api.models import FunctionQuery
from api.realtime import RealtimeVoiceClient
from api.session import RealtimeSession
from api.actions import create_actions, ToolCall
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


@app.post("/api/action")
async def action(query: FunctionQuery) -> List[ToolCall]:
    response = await create_actions(query.carousel, query.input)
    return response


@app.websocket("/api/voice")
async def voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        async with RTLowLevelClient(
            url=AZURE_VOICE_ENDPOINT,
            key_credential=AzureKeyCredential(AZURE_VOICE_KEY),
            azure_deployment="gpt-4o-realtime-preview",
        ) as rt:
            session = RealtimeSession(RealtimeVoiceClient(rt), websocket)
            await session.send_realtime_instructions(prompt)
            tasks = [
                asyncio.create_task(session.start_realtime()),
                asyncio.create_task(session.receive_from_client())
            ]
            await asyncio.gather(*tasks)

    except WebSocketDisconnect as e:
        print(e)
