import json
from typing import Literal, Union
from fastapi import WebSocket
from prompty.tracer import trace
from fastapi import WebSocketDisconnect
from pydantic import BaseModel
from fastapi.websockets import WebSocketState

from openai.resources.beta.realtime.realtime import (
    AsyncRealtimeConnection,
)
from openai.types.beta.realtime.session_update_event import (
    Session,
    SessionTurnDetection,
    SessionInputAudioTranscription,
    # SessionTool,
)
from openai.types.beta.realtime import (
    ErrorEvent,
    SessionCreatedEvent,
    SessionUpdatedEvent,
    ConversationCreatedEvent,
    ConversationItemCreatedEvent,
    ConversationItemInputAudioTranscriptionCompletedEvent,
    ConversationItemInputAudioTranscriptionDeltaEvent,
    ConversationItemInputAudioTranscriptionFailedEvent,
    ConversationItemTruncatedEvent,
    ConversationItemDeletedEvent,
    InputAudioBufferCommittedEvent,
    InputAudioBufferClearedEvent,
    InputAudioBufferSpeechStartedEvent,
    InputAudioBufferSpeechStoppedEvent,
    ResponseCreatedEvent,
    ResponseDoneEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseAudioDeltaEvent,
    ResponseAudioDoneEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    RateLimitsUpdatedEvent,
)

from openai.types.beta.realtime import (
    SessionUpdateEvent,
    InputAudioBufferAppendEvent,
    # InputAudioBufferCommitEvent,
    # InputAudioBufferClearEvent,
    ConversationItemCreateEvent,
    # ConversationItemTruncateEvent,
    # ConversationItemDeleteEvent,
    ResponseCreateEvent,
    # ResponseCancelEvent,
)

from openai.types.beta.realtime import (
    ConversationItem,
    ConversationItemContent,
)


class Message(BaseModel):
    type: Literal[
        "user", "assistant", "audio", "console", "interrupt", "messages", "function"
    ]
    payload: str


class RealtimeClient:
    """
    Realtime client for handling websocket connections and messages.
    """

    def __init__(
        self, realtime: AsyncRealtimeConnection, client: WebSocket, debug: bool = False
    ):
        self.realtime: Union[AsyncRealtimeConnection, None] = realtime
        self.client: Union[WebSocket, None] = client
        self.response_queue: list[ConversationItemCreateEvent] = []
        self.active = True
        self.debug = debug

    async def send_message(self, message: Message):
        if self.client is not None:
            await self.client.send_json(message.model_dump())

    async def send_audio(self, audio: Message):
        # send audio to client, format into bytes
        if (
            self.client is not None
            and self.client.client_state != WebSocketState.DISCONNECTED
        ):
            await self.client.send_json(audio.model_dump())

    async def send_console(self, message: Message):
        if self.client is not None:
            await self.client.send_json(message.model_dump())

    async def update_realtime_session(
        self,
        instructions: str,
        threshold: float = 0.8,
        silence_duration_ms: int = 500,
        prefix_padding_ms: int = 300,
    ):
        if self.realtime is not None:
            session: Session = Session(
                input_audio_format="pcm16",
                turn_detection=SessionTurnDetection(
                    prefix_padding_ms=prefix_padding_ms,
                    silence_duration_ms=silence_duration_ms,
                    threshold=threshold,
                    type="server_vad",
                ),
                input_audio_transcription=SessionInputAudioTranscription(
                    model="whisper-1",
                ),
                voice="sage",
                instructions=instructions,
                modalities=["text", "audio"],
            )
            await self.realtime.send(
                SessionUpdateEvent(
                    type="session.update",
                    session=session,
                )
            )

    @trace
    async def receive_realtime(self):
        # signature = "api.session.RealtimeSession.receive_realtime"
        if self.realtime is None:
            pass

        while self.realtime is not None:
            async for event in self.realtime:
                if "delta" not in event.type and self.debug:
                    print(event.type)
                self.active = True
                match event.type:
                    case "error":
                        await self._handle_error(event)
                    case "session.created":
                        await self._session_created(event)
                    case "session.updated":
                        await self._session_updated(event)
                    case "conversation.created":
                        await self._conversation_created(event)
                    case "conversation.item.created":
                        await self._conversation_item_created(event)
                    case "conversation.item.input_audio_transcription.completed":
                        await self._conversation_item_input_audio_transcription_completed(
                            event
                        )
                    case "conversation.item.input_audio_transcription.delta":
                        await self._conversation_item_input_audio_transcription_delta(
                            event
                        )
                    case "conversation.item.input_audio_transcription.failed":
                        await self._conversation_item_input_audio_transcription_failed(
                            event
                        )
                    case "conversation.item.truncated":
                        await self._conversation_item_truncated(event)
                    case "conversation.item.deleted":
                        await self._conversation_item_deleted(event)
                    case "input_audio_buffer.committed":
                        await self._input_audio_buffer_committed(event)
                    case "input_audio_buffer.cleared":
                        await self._input_audio_buffer_cleared(event)
                    case "input_audio_buffer.speech_started":
                        await self._input_audio_buffer_speech_started(event)
                    case "input_audio_buffer.speech_stopped":
                        await self._input_audio_buffer_speech_stopped(event)
                    case "response.created":
                        await self._response_created(event)
                    case "response.done":
                        await self._response_done(event)
                    case "response.output_item.added":
                        await self._response_output_item_added(event)
                    case "response.output_item.done":
                        await self._response_output_item_done(event)
                    case "response.content_part.added":
                        await self._response_content_part_added(event)
                    case "response.content_part.done":
                        await self._response_content_part_done(event)
                    case "response.text.delta":
                        await self._response_text_delta(event)
                    case "response.text.done":
                        await self._response_text_done(event)
                    case "response.audio_transcript.delta":
                        await self._response_audio_transcript_delta(event)
                    case "response.audio_transcript.done":
                        await self._response_audio_transcript_done(event)
                    case "response.audio.delta":
                        await self._response_audio_delta(event)
                    case "response.audio.done":
                        await self._response_audio_done(event)
                    case "response.function_call_arguments.delta":
                        await self._response_function_call_arguments_delta(event)
                    case "response.function_call_arguments.done":
                        await self._response_function_call_arguments_done(event)
                    case "rate_limits.updated":
                        await self._rate_limits_updated(event)
                    case _:
                        print(
                            f"Unhandled event type {event.type}",
                        )

        self.realtime = None

    @trace(name="error")
    async def _handle_error(self, event: ErrorEvent):
        pass

    @trace(name="session.created")
    async def _session_created(self, event: SessionCreatedEvent):
        await self.send_console(Message(type="console", payload=event.to_json()))

    @trace(name="session.updated")
    async def _session_updated(self, event: SessionUpdatedEvent):
        pass

    @trace(name="conversation.created")
    async def _conversation_created(self, event: ConversationCreatedEvent):
        pass

    @trace(name="conversation.item.created")
    async def _conversation_item_created(self, event: ConversationItemCreatedEvent):
        pass

    @trace(name="conversation.item.input_audio_transcription.completed")
    async def _conversation_item_input_audio_transcription_completed(
        self, event: ConversationItemInputAudioTranscriptionCompletedEvent
    ):
        if event.transcript is not None and len(event.transcript) > 0:
            await self.send_message(Message(type="user", payload=event.transcript))

    @trace(name="conversation.item.input_audio_transcription.delta")
    async def _conversation_item_input_audio_transcription_delta(
        self, event: ConversationItemInputAudioTranscriptionDeltaEvent
    ):
        pass

    @trace(name="conversation.item.input_audio_transcription.failed")
    async def _conversation_item_input_audio_transcription_failed(
        self, event: ConversationItemInputAudioTranscriptionFailedEvent
    ):
        pass

    @trace(name="conversation.item.truncated")
    async def _conversation_item_truncated(self, event: ConversationItemTruncatedEvent):
        pass

    @trace(name="conversation.item.deleted")
    async def _conversation_item_deleted(self, event: ConversationItemDeletedEvent):
        pass

    @trace(name="input_audio_buffer.committed")
    async def _input_audio_buffer_committed(
        self, event: InputAudioBufferCommittedEvent
    ):
        pass

    @trace(name="input_audio_buffer.cleared")
    async def _input_audio_buffer_cleared(self, event: InputAudioBufferClearedEvent):
        pass

    @trace(name="input_audio_buffer.speech_started")
    async def _input_audio_buffer_speech_started(
        self, event: InputAudioBufferSpeechStartedEvent
    ):
        await self.send_console(Message(type="interrupt", payload=""))

    @trace(name="input_audio_buffer.speech_stopped")
    async def _input_audio_buffer_speech_stopped(
        self, event: InputAudioBufferSpeechStoppedEvent
    ):
        pass

    @trace(name="response.created")
    async def _response_created(self, event: ResponseCreatedEvent):
        pass

    @trace(name="response.done")
    async def _response_done(self, event: ResponseDoneEvent):
        if event.response.output is not None and len(event.response.output) > 0:
            output = event.response.output[0]
            match output.type:
                case "message":
                    await self.send_console(
                        Message(
                            type="console",
                            payload=json.dumps(
                                {
                                    "id": output.id,
                                    "role": output.role,
                                    "content": (
                                        output.content[0].transcript
                                        if output.content
                                        else None
                                    ),
                                }
                            ),
                        )
                    )
                case "function_call":
                    await self.send_console(
                        Message(
                            type="function",
                            payload=json.dumps(
                                {
                                    "name": output.name,
                                    "arguments": json.loads(output.arguments or "{}"),
                                    "call_id": output.call_id,
                                    "id": output.id,
                                }
                            ),
                        )
                    )

                case "function_call_output":
                    await self.send_console(
                        Message(type="console", payload=output.model_dump_json())
                    )

        if len(self.response_queue) > 0 and self.realtime is not None:
            for item in self.response_queue:
                await self.realtime.send(item)
            self.response_queue.clear()
            await self.realtime.response.create()

        self.active = False

    @trace(name="response.output_item.added")
    async def _response_output_item_added(self, event: ResponseOutputItemAddedEvent):
        pass

    @trace(name="response.output_item.done")
    async def _response_output_item_done(self, event: ResponseOutputItemDoneEvent):
        pass

    @trace(name="response.content_part.added")
    async def _response_content_part_added(self, event: ResponseContentPartAddedEvent):
        pass

    @trace(name="response.content_part.done")
    async def _response_content_part_done(self, event: ResponseContentPartDoneEvent):
        pass

    @trace(name="response.text.delta")
    async def _response_text_delta(self, event: ResponseTextDeltaEvent):
        pass

    @trace(name="response.text.done")
    async def _response_text_done(self, event: ResponseTextDoneEvent):
        pass

    @trace(name="response.audio.transcript.delta")
    async def _response_audio_transcript_delta(
        self, event: ResponseAudioTranscriptDeltaEvent
    ):
        pass

    @trace(name="response.audio_transcript.done")
    async def _response_audio_transcript_done(
        self, event: ResponseAudioTranscriptDoneEvent
    ):
        if event.transcript is not None and len(event.transcript) > 0:
            await self.send_message(Message(type="assistant", payload=event.transcript))

    @trace(name="response.audio.delta")
    async def _response_audio_delta(self, event: ResponseAudioDeltaEvent):
        await self.send_audio(Message(type="audio", payload=event.delta))

    @trace(name="response.audio.done")
    async def _response_audio_done(self, event: ResponseAudioDoneEvent):
        pass

    @trace(name="response.function_call_arguments.delta")
    async def _response_function_call_arguments_delta(
        self, event: ResponseFunctionCallArgumentsDeltaEvent
    ):
        pass

    @trace(name="response.function_call_arguments.done")
    async def _response_function_call_arguments_done(
        self, event: ResponseFunctionCallArgumentsDoneEvent
    ):
        pass

    @trace(name="rate_limits.updated")
    async def _rate_limits_updated(self, event: RateLimitsUpdatedEvent):
        pass

    @trace
    async def receive_client(self):
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
                        await self.realtime.send(
                            InputAudioBufferAppendEvent(
                                type="input_audio_buffer.append", audio=m.payload
                            )
                        )
                    case "user":
                        await self.realtime.send(
                            ConversationItemCreateEvent(
                                type="conversation.item.create",
                                item=ConversationItem(
                                    role="user",
                                    type="message",
                                    content=[
                                        ConversationItemContent(
                                            type="input_text",
                                            text=m.payload,
                                        )
                                    ],
                                ),
                            )
                        )
                    case "interrupt":
                        await self.realtime.send(
                            ResponseCreateEvent(type="response.create")
                        )
                    case "function":
                        function_message = json.loads(m.payload)

                        await self.realtime.send(
                            ConversationItemCreateEvent(
                                type="conversation.item.create",
                                item=ConversationItem(
                                    call_id=function_message["call_id"],
                                    type="function_call_output",
                                    output=function_message["output"],
                                ),
                            )
                        )

                        await self.realtime.response.create()

                    case _:
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

    @property
    def closed(self):
        if self.client is None:
            return True
        return self.client.client_state == WebSocketState.DISCONNECTED
