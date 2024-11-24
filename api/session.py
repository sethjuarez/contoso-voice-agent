import json
from typing import Literal
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from prompty.tracer import Tracer
from pydantic import BaseModel
from rtclient import RTLowLevelClient
from api.realtime import RealtimeVoiceClient


class Message(BaseModel):
    type: Literal["user", "assistant", "audio", "console"]
    payload: str


class RealtimeSession:

    def __init__(self, realtime: RealtimeVoiceClient, client: WebSocket):
        self.realtime: RealtimeVoiceClient = realtime
        self.client: WebSocket = client

    async def send_message(self, message: Message):
        #print("sending message", message.model_dump_json())
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
            print("waiting for message")
            async for message in self.realtime.receive_message():
                print("received message", message.type)
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

                    case "turn_detected":
                        pass

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
                            self.send_console(
                                Message(type="console", payload=message.content)
                            )
                    case _:
                        with Tracer.start("unhandled_message") as t:
                            t("message", message)
                            self.send_console(
                                Message(type="console", payload="Unhandled message")
                            )

        self.realtime = None

    async def receive_client(self):
        while self.client.client_state != WebSocketState.DISCONNECTED:
            message = await self.client.receive_text()
            
            message_json = json.loads(message)
            m =  Message(**message_json)
            #print("received message", m.type)
            match m.type:
                case "audio":
                    await self.realtime.send_audio_message(m.payload)
                case _:
                    await self.send_console(Message(type="console", payload="Unhandled message"))
