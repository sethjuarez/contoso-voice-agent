export interface Message {
  type: "user" | "assistant" | "audio" | "console" | "interrupt" | "messages";
  payload: string;
}


export interface SimpleMessage {
  name: string;
  text: string;
}