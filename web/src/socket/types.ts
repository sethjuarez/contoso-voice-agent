export interface Message {
  type: "user" | "assistant" | "audio" | "console";
  payload: string;
}
