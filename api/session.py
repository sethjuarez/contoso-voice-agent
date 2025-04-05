import json
from typing import Dict, List, Union
from fastapi import WebSocket
from prompty.tracer import trace
from prompty.tracer import Tracer
from fastapi.websockets import WebSocketState
from api.chat import create_response
from api.models import (
    ClientMessage,
    send_action,
    send_context,
    start_assistant,
    stop_assistant,
    stream_assistant,
)

from api.voice import RealtimeClient, Message


class ChatSession:
    def __init__(self, client: WebSocket):
        self.client = client
        self.realtime: Union[RealtimeClient, None] = None
        self.context: List[str] = []

    async def send_message(self, message: Message):
        await self.client.send_json(message.model_dump())

    def add_realtime(self, realtime: RealtimeClient):
        self.realtime = realtime

    def is_closed(self):
        client_closed = (
            self.client is None
            or self.client.client_state == WebSocketState.DISCONNECTED
        )
        realtime_closed = (
            self.realtime is None
            or self.realtime is None
            or self.realtime.closed
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
                response = await create_response(
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
