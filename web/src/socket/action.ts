import { ChatState } from "@/store/chat";
import { ContextState } from "@/store/context";
import { Action, Assistant, Context, SocketMessage } from "@/store/socket";

export class ActionClient {
  assistantName: string = "Wiry";
  state: ChatState;
  context: ContextState;
  constructor(state: ChatState, context: ContextState) {
    this.state = state;
    this.context = context;
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
