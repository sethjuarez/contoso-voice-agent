/**
 * Represents a message in the chat system with its type and payload.
 */
export interface Message {
  /** The type of message indicating its source and purpose */
  type: "user" | "assistant" | "audio" | "console" | "interrupt" | "messages";
  /** The actual message content */
  payload: string;
}

/**
 * A simplified message format used for basic text communication.
 */
export interface SimpleMessage {
  /** The name/identifier of the message sender */
  name: string;
  /** The text content of the message */
  text: string;
}