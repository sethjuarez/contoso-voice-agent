import { ChatState, Turn } from "@/store/chat";
import { ContextState } from "@/store/context";
import { Action, Assistant, Context, SocketMessage } from "@/store/socket";
import { SimpleMessage } from "./types";
import { API_ENDPOINT } from "@/store/endpoint";


export const suggestionRequested = async (messages: SimpleMessage[]) => {
  const configuration = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(messages),
  };

  const endpoint = API_ENDPOINT.endsWith("/")
    ? API_ENDPOINT.slice(0, -1)
    : API_ENDPOINT;

  const url = `${endpoint}/api/request`;
  const response = await fetch(url, configuration);
  const json = await response.json();
  return json;
};

export const startSuggestionTask = async (
  messages: SimpleMessage[]
): Promise<{
  [Symbol.asyncIterator](): AsyncGenerator<string, void, unknown>;
}> => {
  console.log("startSuggestionTask", messages);
  const configuration = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Connection: "keep-alive",
    },
    body: JSON.stringify(messages),
  };

  const endpoint = API_ENDPOINT.endsWith("/")
    ? API_ENDPOINT.slice(0, -1)
    : API_ENDPOINT;

  const url = `${endpoint}/api/suggestion`;
  console.log("startSuggestionTask", url, configuration);

  const response = await fetch(url, configuration);
  const reader = response.body?.getReader();
  if (!reader) {
    return {
      async *[Symbol.asyncIterator]() {
        return;
      },
    };
  }

  return {
    async *[Symbol.asyncIterator]() {
      let readResult = await reader.read();
      while (!readResult.done) {
        yield new TextDecoder().decode(readResult.value);
        readResult = await reader.read();
      }
    },
  };
};

export class ActionClient {
  assistantName: string = "Wiry";
  state: ChatState;
  context: ContextState;
  constructor(state: ChatState, context: ContextState) {
    this.state = state;
    this.context = context;
  }

  sendVoiceUserMessage(message: string) {
    const turn: Turn = {
      name: "Seth Juarez",
      avatar: "/people/sethjuarez.jpg",
      image: null,
      message: message,
      status: "voice",
      type: "user",
    };
    this.state.sendFullMessage(turn);
  }

  sendVoiceAssistantMessage(message: string) {
    const turn: Turn = {
      name: this.assistantName,
      avatar: null,
      image: null,
      message: message,
      status: "voice",
      type: "assistant",
    };
    this.state.sendFullMessage(turn);
  }

  execute(message: SocketMessage) {
    switch (message.type) {
      case "assistant":
        this.executeAssistant(message.payload as Assistant);
        break;
      case "context":
        this.executeContext(message.payload as Context);
        break;
      case "action":
        this.executeAction(message.payload as Action);
        break;
    }
  }

  executeAssistant(message: Assistant) {
    switch (message.state) {
      case "start":
        this.state.startAssistantMessage(this.assistantName);
        break;
      case "stream":
        this.state.streamAssistantMessage(message.payload || "");
        break;
      case "complete":
        this.state.completeAssistantMessage();
        break;
      case "full":
        this.state.addAssistantMessage(
          this.assistantName,
          message.payload || ""
        );
        break;
    }
  }

  executeContext(message: Context) {
    console.log("CONTEXT", message);
    switch (message.type) {
      case "action":
        break;
      case "user":
        this.context.addContext(message.payload);
        break;
      case "issue":
        break;
      case "article":
        break;
    }
  }

  executeAction(message: Action) {
    const args = JSON.parse(message.arguments);
    console.log("ACTION", message.name, args);
    switch (message.name) {
      case "call":
        this.context.setCallScore(args.score);
        break;
    }
  }
}
