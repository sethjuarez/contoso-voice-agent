# Voice + Text Configurator

A WebSocket-based voice and text configuration system that enables real-time communication between clients and a server.

## Key Components

### WebSocket Client API
The core WebSocket client (`WebSocketClient`) provides bidirectional communication:

```typescript
import { WebSocketClient } from './web/src/socket/websocket-client';

// Create client with message type parameters
const client = new WebSocketClient<RequestMsg, ResponseMsg>("ws://server");

// Send messages
await client.send({type: "request", data: "..."});

// Receive messages asynchronously
for await (const msg of client) {
  console.log("Received:", msg);
}

// Close when done
await client.close();
```

### Action System
The `ActionClient` handles application-specific messaging and state management:

```typescript
import { ActionClient } from './web/src/socket/action';

const client = new ActionClient(chatState, contextState);

// Send voice messages
client.sendVoiceUserMessage("Hello");
client.sendVoiceAssistantMessage("Hi there");

// Handle suggestions
client.streamSuggestion("suggestion text");
```

## Message Types

- `Message`: Core message type with type and payload
- `SimpleMessage`: Basic text message format
- Custom message types for specific actions

For detailed API documentation, see the JSDoc comments in:
- web/src/socket/websocket-client.ts
- web/src/socket/action.ts 
- web/src/socket/types.ts
