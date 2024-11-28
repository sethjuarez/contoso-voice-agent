export interface Message {
  type: "user" | "assistant" | "audio" | "console" | "interrupt";
  payload: string;
}
