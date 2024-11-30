export interface Message {
  type: "user" | "assistant" | "audio" | "console" | "interrupt";
  payload: string;
}


export interface SimpleMessage {
  name: string;
  text: string;
}