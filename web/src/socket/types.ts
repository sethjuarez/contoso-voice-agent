export interface Message {
  type: "user" | "assistant" | "audio" | "console" | "interrupt" | "messages" | "function";
  payload: string;
}


export interface SimpleMessage {
  name: string;
  text: string;
}