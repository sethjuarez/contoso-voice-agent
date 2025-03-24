from realtime_chat.core.models import (
    ClientMessage,
    send_action,
    send_context, 
    start_assistant,
    stop_assistant,
    stream_assistant,
)

import asyncio
import json
from typing import Dict, List, Literal, Union, Any
from fastapi import WebSocket
from prompty.tracer import trace
from fastapi import WebSocketDisconnect
from pydantic import BaseModel
from prompty.tracer import Tracer
from fastapi.websockets import WebSocketState
from realtime_chat.core.voice import RealtimeVoiceClient

# Mock response for testing
async def mock_create_response(name: str, text: str, context: List[str], image: str | None) -> Dict[str, Any]:
    return {
        "response": "Test response",
        "context": "Test context",
        "call": 0.8
    }


class Message(BaseModel):
    type: Literal["user", "assistant", "audio", "console", "interrupt", "messages"]
    payload: str


class RealtimeSession:

    def __init__(self, realtime: RealtimeVoiceClient, client: WebSocket):
        self.realtime: Union[RealtimeVoiceClient, None] = realtime
        self.client: Union[WebSocket, None] = client

    async def send_message(self, message: Message):
        if self.client is not None:
            await self.client.send_json(message.model_dump())

    async def send_audio(self, audio: Message):
        # send audio to client, format into bytes
        if self.client is not None:
            await self.client.send_json(audio.model_dump())

    async def send_console(self, message: Message):
        if self.client is not None:
            await self.client.send_json(message.model_dump())

    async def send_realtime_instructions(
        self,
        instructions: Union[str | None] = None,
        threshold: float = 0.8,
        silence_duration_ms: int = 500,
        prefix_padding_ms: int = 300,
    ):
        if self.realtime is not None:
            await self.realtime.send_session_update(
                instructions, threshold, silence_duration_ms, prefix_padding_ms
            )

    @trace
    async def receive_realtime(self):
        signature = "api.session.RealtimeSession.receive_realtime"
        while self.realtime is not None and not self.realtime.closed:
            async for message in self.realtime.receive_message():
                # print("received message", message.type)
                if message is None:
                    continue

                match message.type:
                    case "session.created":
                        with Tracer.start("session_created") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, message.content)
                            await self.send_console(
                                Message(
                                    type="console", payload=json.dumps(message.content)
                                )
                            )
                    case "conversation.item.input_audio_transcription.completed":
                        with Tracer.start("receive_user_transcript") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "conversation.item.input_audio_transcription.completed",
                                    "role": "user",
                                    "content": message.content,
                                },
                            )
                            if (
                                message.content is not None
                                and isinstance(message.content, str)
                                and message.content != ""
                            ):
                                await self.send_message(
                                    Message(type="user", payload=message.content)
                                )

                    case "response.audio_transcript.done":
                        with Tracer.start("receive_assistant_transcript") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "response.audio_transcript.done",
                                    "role": "assistant",
                                    "content": message.content,
                                },
                            )
                            if (
                                message.content is not None
                                and isinstance(message.content, str)
                                and message.content != ""
                            ):
                                # audio stream
                                await self.send_message(
                                    Message(type="assistant", payload=message.content)
                                )

                    case "response.audio.delta":
                        if (
                            message.content is not None
                            and isinstance(message.content, str)
                            and message.content != ""
                        ):
                            await self.send_audio(
                                Message(type="audio", payload=message.content)
                            )

                    case "response.failed":
                        with Tracer.start("realtime_failure") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "failure": message.content,
                                },
                            )
                            print("Realtime failure", message.content)

                    case "turn_detected":
                        # send interrupt message
                        with Tracer.start("turn_detected") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "turn_detected",
                                    "content": message.content,
                                },
                            )
                            await self.send_console(
                                Message(type="interrupt", payload="")
                            )
                    case _:
                        with Tracer.start("unhandled_message") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(
                                Tracer.INPUTS,
                                {
                                    "type": "unhandled_message",
                                    "content": message.content,
                                },
                            )
                            await self.send_console(
                                Message(type="console", payload="Unhandled message")
                            )

        self.realtime = None

    @trace
    async def receive_client(self):
        signature = "api.session.RealtimeSession.receive_client"
        if self.client is None or self.realtime is None:
            return
        try:
            while self.client.client_state != WebSocketState.DISCONNECTED:
                message = await self.client.receive_text()

                message_json = json.loads(message)
                m = Message(**message_json)
                # print("received message", m.type)
                match m.type:
                    case "audio":
                        await self.realtime.send_audio_message(m.payload)
                    case "user":
                        with Tracer.start("user_message") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, m.model_dump())
                            await self.realtime.send_user_message(m.payload)
                    case "interrupt":
                        with Tracer.start("trigger_response") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, m.model_dump())
                            await self.realtime.trigger_response()
                    case _:
                        with Tracer.start("user_message") as t:
                            t(Tracer.SIGNATURE, signature)
                            t(Tracer.INPUTS, m.model_dump())
                            await self.send_console(
                                Message(type="console", payload="Unhandled message")
                            )
        except WebSocketDisconnect:
            print("Realtime Socket Disconnected")

    async def close(self):
        if self.client is None or self.realtime is None:
            return
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
        self.realtime: Union[RealtimeSession, None] = None
        self.context: List[str] = []

    async def send_message(self, message: Message):
        await self.client.send_json(message.model_dump())

    def add_realtime(self, realtime: RealtimeSession):
        self.realtime = realtime

    def is_closed(self):
        client_closed = (
            self.client is None
            or self.client.client_state == WebSocketState.DISCONNECTED
        )
        realtime_closed = (
            self.realtime is None
            or self.realtime.realtime is None
            or self.realtime.realtime.closed
        )
        return client_closed and realtime_closed

    @trace
    async def receive_chat(self):
        while (
            self.client is not None
            and self.client.client_state != WebSocketState.DISCONNECTED
        ):
            with Tracer.start("chat_turn") as t:
                t(Tracer.SIGNATURE, "api.session.ChatSession.start_chat")
                message = await self.client.receive_json()
                msg = ClientMessage(**message)

                t(
                    Tracer.INPUTS,
                    {
                        "request": msg.text,
                        "image": msg.image is not None,
                    },
                )

                # start assistant
                await self.client.send_json(start_assistant())

                # create response
                response = await mock_create_response(
                    msg.name, msg.text, self.context, msg.image
                )

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
                t(
                    Tracer.RESULT,
                    {
                        "response": text,
                        "context": context,
                        "call": call,
                    },
                )

    async def start_realtime(self, prompt: str):
        if self.realtime is None:
            raise Exception("Realtime session not available")

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

    @classmethod
    async def clear_closed_sessions(cls):
        threads = cls.sessions.keys()
        for thread_id in threads:
            if cls.sessions[thread_id].is_closed():
                try:
                    del cls.sessions[thread_id]
                except Exception as e:
                    print(f"Error closing session ({thread_id})", e)
