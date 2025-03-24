"""
Real-time Voice Communication Module

This module implements real-time voice communication functionality using Azure's
real-time voice services. It handles:
- Audio stream management
- Voice activity detection (VAD)
- Message processing and routing
- Real-time transcription and response generation
"""

from dataclasses import dataclass
from typing import Any, AsyncGenerator, Union
from prompty.tracer import trace

from rtclient import (  # type: ignore
    InputAudioBufferAppendMessage,
    InputAudioBufferClearMessage,
    InputAudioTranscription,
    ItemCreateMessage,
    RTLowLevelClient,
    ResponseCreateMessage,
    ResponseCreateParams,
    ServerVAD,
    SessionUpdateMessage,
    SessionUpdateParams,
    SystemMessageItem,
    UserMessageItem,
) 


@dataclass
class RealTimeItem:
    """
    Represents a real-time communication item.
    
    Attributes:
        type: Type of the item (e.g., 'audio', 'text', 'response')
        content: Optional content payload
    """
    type: str
    content: Any | None = None


class RealtimeVoiceClient:
    """
    Handles real-time voice communication with Azure services.
    
    This class manages the bidirectional voice communication stream, including:
    - Audio input/output
    - Message processing
    - Voice activity detection
    - Transcription handling
    - Response generation
    
    Attributes:
        client: The low-level RT client for Azure communication
        verbose: Whether to enable detailed logging
    """

    def __init__(self, client: RTLowLevelClient = None, verbose: bool = False):
        self.client: RTLowLevelClient = client
        self.verbose: bool = verbose

    def set_client(self, client: RTLowLevelClient):
        """Set the RT client instance for this voice client."""
        self.client = client

    @property
    def closed(self):
        """Check if the client connection is closed."""
        return self.client is None or self.client.closed

    async def close(self):
        """Close the client connection gracefully."""
        if self.client is not None:
            await self.client.close()

    async def send_user_message(self, message: str):
        """
        Send a user text message to the voice service.
        
        Args:
            message: The text message to send
            
        Raises:
            Exception: If client is not initialized or message is empty
        """
        if self.client is None:
            raise Exception("Client not set")

        if message is None or len(message) == 0:
            return

        await self.client.send(
            ItemCreateMessage(
                item=UserMessageItem(
                    role="user",
                    content=[
                        {
                            "type": "input_text",
                            "text": message,
                        }
                    ],
                )
            )
        )

    @trace
    async def send_user_message_with_response(self, message: str):
        """
        Send a user message and request an immediate response.
        
        This method sends a user message and configures the system to generate
        a response right away, unlike send_user_message which only sends the message.
        
        Args:
            message: The text message to send
            
        Raises:
            Exception: If client is not initialized or message is empty
        """
        if self.client is None:
            raise Exception("Client not set")

        if message is None or len(message) == 0:
            return

        response = ResponseCreateParams(
            input_items=[
                UserMessageItem(
                    content=ItemCreateMessage(
                        item=UserMessageItem(
                            role="user",
                            content=[
                                {
                                    "type": "input_text",
                                    "text": message,
                                }
                            ],
                        )
                    )
                )
            ]
        )

        await self.client.send(ResponseCreateMessage(response=response))

    async def trigger_response(self):
        """
        Trigger the generation of a response without sending new input.
        
        Raises:
            Exception: If client is not initialized
        """
        if self.client is None:
            raise Exception("Client not set")
        await self.client.send(ResponseCreateMessage())

    @trace
    async def send_system_message(self, message: str):
        """
        Send a system message to configure or control the voice service.
        
        System messages provide context and configuration rather than user input.
        
        Args:
            message: The system message text
            
        Raises:
            Exception: If client is not initialized or message is empty
        """
        if self.client is None:
            raise Exception("Client not set")

        if message is None or len(message) == 0:
            return

        await self.client.send(
            ItemCreateMessage(
                item=SystemMessageItem(
                    role="system",
                    content=[
                        {
                            "type": "input_text",
                            "text": message,
                        }
                    ],
                )
            )
        )

    @trace
    async def send_session_update(
        self,
        instructions: Union[str | None] = None,
        threshold: float = 0.8,
        silence_duration_ms: int = 500,
        prefix_padding_ms: int = 300,
    ):
        """
        Update the voice session configuration.
        
        Args:
            instructions: Optional system instructions for the session
            threshold: Voice activity detection threshold (0.0-1.0)
            silence_duration_ms: Duration of silence to detect end of speech
            prefix_padding_ms: Audio padding before speech detection
            
        Raises:
            Exception: If client is not initialized
        if self.client is None:
            raise Exception("Client not set")

        session = SessionUpdateParams(
            turn_detection=ServerVAD(
                type="server_vad",
                threshold=threshold,
                silence_duration_ms=silence_duration_ms,
                prefix_padding_ms=prefix_padding_ms,
            ),
            input_audio_transcription=InputAudioTranscription(model="whisper-1"),
            voice="shimmer",
            instructions=instructions,
            modalities={"audio", "text"},
        )

        await self.client.send(SessionUpdateMessage(session=session))

    async def send_audio_message(self, audio_data: Any):
        if self.client is None:
            raise Exception("Client not set")

        if audio_data is None or len(audio_data) == 0:
            return

        await self.client.send(InputAudioBufferAppendMessage(audio=audio_data))

    async def receive_message(self) -> AsyncGenerator[RealTimeItem, None]:
        if self.client is None:
            raise Exception("Client not set")

        message = await self.client.recv()
        if message is None:
            return

        match message.type:
            case "session.created":
                if self.verbose:
                    print("Session Created Message")
                    print(f"  Model: {message.session.model}")
                    print(f"  Session Id: {message.session.id}")

                    yield RealTimeItem(
                        type="session.created",
                        content={
                            "model": message.session.model,
                            "session": message.session.id,
                        },
                    )

            case "error":
                if self.verbose:
                    print("Error Message")
                    print(f"  Error: {message.error}")

            case "input_audio_buffer.committed":
                if self.verbose:
                    print("Input Audio Buffer Committed Message")
                    print(f"  Item Id: {message.item_id}")

            case "input_audio_buffer.cleared":
                if self.verbose:
                    print("Input Audio Buffer Cleared Message")

            case "input_audio_buffer.speech_started":
                if self.verbose:
                    print("Input Audio Buffer Speech Started Message")
                    print(f"  Item Id: {message.item_id}")
                    print(f"  Audio Start [ms]: {message.audio_start_ms}")

                yield RealTimeItem(type="turn_detected")
                await self.client.send(InputAudioBufferClearMessage())

            case "input_audio_buffer.speech_stopped":
                if self.verbose:
                    print("Input Audio Buffer Speech Stopped Message")
                    print(f"  Item Id: {message.item_id}")
                    print(f"  Audio End [ms]: {message.audio_end_ms}")

            case "conversation.item.created":
                if self.verbose:
                    print("Conversation Item Created Message")
                    print(f"  Id: {message.item.id}")
                    print(f"  Previous Id: {message.previous_item_id}")
                    if message.item.type == "message":
                        print(f"  Role: {message.item.role}")
                        for index, content in enumerate(message.item.content):
                            print(f"  [{index}]:")
                            print(f"    Content Type: {content.type}")
                            if content.type == "input_text" or content.type == "text":
                                print(f"  Text: {content.text}")
                            elif (
                                content.type == "input_audio" or content.type == "audio"
                            ):
                                print(f"  Audio Transcript: {content.transcript}")

            case "conversation.item.truncated":
                if self.verbose:
                    print("Conversation Item Truncated Message")
                    print(f"  Id: {message.item_id}")
                    print(f" Content Index: {message.content_index}")
                    print(f"  Audio End [ms]: {message.audio_end_ms}")

            case "conversation.item.deleted":
                if self.verbose:
                    print("Conversation Item Deleted Message")
                    print(f"  Id: {message.item_id}")

            case "conversation.item.input_audio_transcription.completed":
                if self.verbose:
                    print("Input Audio Transcription Completed Message")
                    print(f"  Id: {message.item_id}")
                    print(f"  Content Index: {message.content_index}")
                    print(f"  Transcript: {message.transcript}")

                text = message.transcript.strip()
                if text and len(text) > 0:
                    yield RealTimeItem(
                        type="conversation.item.input_audio_transcription.completed",
                        content=text,
                    )

            case "conversation.item.input_audio_transcription.failed":
                if self.verbose:
                    print("Input Audio Transcription Failed Message")
                    print(f"  Id: {message.item_id}")
                    print(f"  Error: {message.error}")

            case "response.created":
                if self.verbose:
                    print("Response Created Message")
                    print(f"  Response Id: {message.response.id}")
                    print("  Output Items:")
                    for index, item in enumerate(message.response.output):
                        print(f"  [{index}]:")
                        print(f"    Item Id: {item.id}")
                        print(f"    Type: {item.type}")
                        if item.type == "message":
                            print(f"    Role: {item.role}")
                            match item.role:
                                case "system":
                                    for content_index, content in enumerate(
                                        item.content
                                    ):
                                        print(f"    [{content_index}]:")
                                        print(f"      Content Type: {content.type}")
                                        print(f"      Text: {content.text}")
                                case "user":
                                    for content_index, content in enumerate(
                                        item.content
                                    ):
                                        print(f"    [{content_index}]:")
                                        print(f"      Content Type: {content.type}")
                                        if content.type == "input_text":
                                            print(f"      Text: {content.text}")
                                        elif content.type == "input_audio":
                                            print(
                                                f"      Audio Data Length: {len(content.audio)}"
                                            )
                                case "assistant":
                                    for content_index, content in enumerate(
                                        item.content
                                    ):
                                        print(f"    [{content_index}]:")
                                        print(f"      Content Type: {content.type}")
                                        print(f"      Text: {content.text}")
                        elif item.type == "function_call":
                            print(f"    Call Id: {item.call_id}")
                            print(f"    Function Name: {item.name}")
                            print(f"    Parameters: {item.arguments}")
                        elif item.type == "function_call_output":
                            print(f"    Call Id: {item.call_id}")
                            print(f"    Output: {item.output}")

            case "response.done":
                if self.verbose:
                    print("Response Done Message")
                    print(f"  Response Id: {message.response.id}")

                if message.response.status_details:
                    if self.verbose:
                        print(
                            f"  Status Details: {message.response.status_details.model_dump_json()}"
                        )

                    if (
                        message.response.status_details.type == "cancelled"
                        and message.response.status_details.reason == "turn_detected"
                    ):
                        if self.verbose:
                            print("  Turn Detected - flusing ACS")

                        yield RealTimeItem(type="turn_detected")
                        await self.client.send(InputAudioBufferClearMessage())

                    elif message.response.status_details.type == "failed":
                        if self.verbose:
                            print("  Response Failed")

                        yield RealTimeItem(
                            type="response.failed",
                            content=message.response.status_details.model_dump(),
                        )

            case "response.output_item.added":
                if self.verbose:
                    print("Response Output Item Added Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Item Id: {message.item.id}")

            case "response.output_item.done":
                if self.verbose:
                    print("Response Output Item Done Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Item Id: {message.item.id}")

            case "response.content_part.added":
                if self.verbose:
                    print("Response Content Part Added Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Item Id: {message.item_id}")

            case "response.content_part.done":
                if self.verbose:
                    print("Response Content Part Done Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  ItemPart Id: {message.item_id}")

            case "response.text.delta":
                if self.verbose:
                    print("Response Text Delta Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Text: {message.delta}")

            case "response.text.done":
                if self.verbose:
                    print("Response Text Done Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Text: {message.text}")

            case "response.audio_transcript.delta":
                if self.verbose:
                    print("Response Audio Transcript Delta Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Item Id: {message.item_id}")
                    print(f"  Transcript: {message.delta}")

            case "response.audio_transcript.done":
                if self.verbose:
                    print("Response Audio Transcript Done Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Item Id: {message.item_id}")
                    print(f"  Transcript: {message.transcript}")

                # only yield if there is content
                text = message.transcript.strip()
                if text and len(text) > 0:
                    yield RealTimeItem(
                        type="response.audio_transcript.done",
                        content=text,
                    )

            case "response.audio.delta":
                if self.verbose:
                    print("Response Audio Delta Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Item Id: {message.item_id}")
                    print(f"  Audio Data Length: {len(message.delta)}")

                yield RealTimeItem(
                    type="response.audio.delta",
                    content=message.delta,
                )

            case "response.audio.done":
                if self.verbose:
                    print("Response Audio Done Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Item Id: {message.item_id}")

            case "response.function_call_arguments.delta":
                if self.verbose:
                    print("Response Function Call Arguments Delta Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Arguments: {message.delta}")

            case "response.function_call_arguments.done":
                if self.verbose:
                    print("Response Function Call Arguments Done Message")
                    print(f"  Response Id: {message.response_id}")
                    print(f"  Arguments: {message.arguments}")

            case "rate_limits.updated":
                if self.verbose:
                    print("Rate Limits Updated Message")
                    print(f"  Rate Limits: {message.rate_limits}")
            case _:
                if self.verbose:
                    print("Unknown Message")
