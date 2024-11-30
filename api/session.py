import asyncio
import json
from pathlib import Path
from typing import Dict, List, Literal
from fastapi import WebSocket
from pydantic import BaseModel
from prompty.tracer import Tracer
from fastapi.websockets import WebSocketState
from api.chat import create_response
from api.models import ClientMessage, full_assistant, send_action, send_context, start_assistant, stop_assistant, stream_assistant
from api.realtime import RealtimeVoiceClient


class Message(BaseModel):
    type: Literal["user", "assistant", "audio", "console", "interrupt", "messages"]
    payload: str


class RealtimeSession:

    def __init__(self, realtime: RealtimeVoiceClient, client: WebSocket):
        self.realtime: RealtimeVoiceClient = realtime
        self.client: WebSocket = client

    async def send_message(self, message: Message):
        await self.client.send_json(message.model_dump())

    async def send_audio(self, audio: Message):
        # send audio to client, format into bytes
        await self.client.send_json(audio.model_dump())

    async def send_console(self, message: Message):
        await self.client.send_json(message.model_dump())

    async def send_realtime_instructions(self, instructions: str):
        await self.realtime.send_session_update(instructions)

    async def receive_realtime(self):
        while self.realtime != None and not self.realtime.closed:
            async for message in self.realtime.receive_message():
                # print("received message", message.type)
                if message is None:
                    continue

                match message.type:
                    case "conversation.item.input_audio_transcription.completed":
                        with Tracer.start("receive_user_transcript") as t:
                            t("message", message.content)
                            t("role", "user")
                            await self.send_message(
                                Message(type="user", payload=message.content)
                            )

                    case "response.audio_transcript.done":
                        with Tracer.start("receive_assistant_transcript") as t:
                            t("message", message.content)
                            t("role", "assistant")
                            # audio stream
                            await self.send_message(
                                Message(type="assistant", payload=message.content)
                            )

                    case "response.audio.delta":
                        await self.send_audio(
                            Message(type="audio", payload=message.content)
                        )

                    case "response.failed":
                        with Tracer.start("realtime_failure") as t:
                            t("failure", message.content)
                            print("Realtime failure", message.content)
                            
                    case "turn_detected":
                        # send interrupt message
                        # print("turn detected")
                        await self.send_console(
                            Message(type="interrupt", payload="")
                        )
                    case _:
                        with Tracer.start("unhandled_message") as t:
                            t("message", message)
                            await self.send_console(
                                Message(type="console", payload="Unhandled message")
                            )

        self.realtime = None

    async def receive_client(self):
        while self.client.client_state != WebSocketState.DISCONNECTED:
            message = await self.client.receive_text()

            message_json = json.loads(message)
            m = Message(**message_json)
            # print("received message", m.type)
            match m.type:
                case "audio":
                    await self.realtime.send_audio_message(m.payload)
                case "user":
                    await self.realtime.send_user_message(m.payload)
                case "interrupt":
                    await self.realtime.trigger_response()
                case _:
                    await self.send_console(
                        Message(type="console", payload="Unhandled message")
                    )

    async def close(self):
        try:
            await self.client.close()
            await self.realtime.close()
        except Exception as e:
            print("Error closing session", e)
            self.client = None
            self.realtime = None


class ChatSession:
    def __init__(self, client: WebSocket):
        self.client = client
        self.realtime: RealtimeSession = None
        self.context: List[str] = []

    async def send_message(self, message: Message):
        await self.client.send_json(message.model_dump())

    def add_realtime(self, realtime: RealtimeSession):
        self.realtime = realtime

    async def start_chat(self):
        try:
            while (
                self.client != None
                and self.client.client_state != WebSocketState.DISCONNECTED
            ):
                message = await self.client.receive_json()
                msg = ClientMessage(**message)

                # start assistant
                await self.client.send_json(start_assistant())

                # create response
                response = await create_response(msg.name, msg.text, self.context, msg.image)

                # unpack response
                text = response["response"]
                context = response["context"]
                call = response["call"]

                # send response
                await self.client.send_json(stream_assistant(text))
                await self.client.send_json(stop_assistant())

                # send context
                await self.client.send_json(send_context(context))
                await self.client.send_json(
                    send_action("call", json.dumps({"score": call}))
                )
                self.context.append(response["context"])

        except Exception as e:
            print("Error in chat session", e)

    async def start_realtime(self, prompt: str):
        await self.realtime.send_realtime_instructions(prompt)
        tasks = [
            asyncio.create_task(self.realtime.receive_realtime()),
            asyncio.create_task(self.realtime.receive_client()),
        ]
        await asyncio.gather(*tasks)

    async def close(self):
        await self.client.close()
        if self.realtime:
            await self.realtime.close()


class SessionManager:
    sessions: Dict[str, ChatSession] = {}

    @classmethod
    async def create_session(cls, thread_id: str, socket: WebSocket) -> ChatSession:
        session = ChatSession(socket)
        cls.sessions[thread_id] = session
        return session

    @classmethod
    def get_session(cls, thread_id: str):
        if thread_id in cls.sessions:
            return cls.sessions[thread_id]
        return None

    @classmethod
    async def close_session(cls, thread_id: str):
        if thread_id in cls.sessions:
            await cls.sessions[thread_id].close()
            del cls.sessions[thread_id]

    @classmethod
    async def clear_sessions(cls):
        for thread_id in cls.sessions:
            try:
                await cls.sessions[thread_id].close()
            except Exception as e:
                print(f"Error closing session ({thread_id})", e)
        cls.sessions = {}
