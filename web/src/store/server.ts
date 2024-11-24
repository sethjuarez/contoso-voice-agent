/**
 * Function for mapping Turns to messages
 */

import { Turn } from "./chat";
import { fetchCachedImage } from "./images";
import { Message } from "./socket";



export const mapTurnToMessage = async (turn: Turn, process: (message: Message) => void, context: string[] = []) => {
  console.log("Turn", turn);
  const message: Message = {
    name: turn.name,
    text: turn.message,
    context: context,
  };

  if (turn.image) {
    console.log("Fetching image", turn.image);
    await fetchCachedImage(turn.image, (img) => {
      console.log("Fetched image", img);
      message.image = img;
      process(message);
    });
  } else {
    process(message);
  }
}

export interface Response {
  context: string;
  message: string;
}

export class StreamingServer {
  endpoint: string;
  constructor(endpoint: string) {
    // remove trailing slash
    this.endpoint = endpoint.endsWith("/") ? endpoint.slice(0, -1) : endpoint;
  }

  readChunks(reader: ReadableStreamDefaultReader<Uint8Array>) {
    return {
      async *[Symbol.asyncIterator]() {
        let readResult = await reader.read();
        while (!readResult.done) {
          yield readResult.value;
          readResult = await reader.read();
        }
      },
    };
  }

  async post(route: string, message: Message, consume: (chunk: Response) => void) {

    console.log("Message", JSON.stringify(message));

    route = route.startsWith("/") ? route : "/" + route;
    const configuration = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Connection: "keep-alive",
      },
      body: JSON.stringify(message),
    };

    const response = await fetch(this.endpoint + route, configuration);
    const reader = response.body?.getReader();
    if (!reader) throw new Error("No reader found in response body");
    for await (const chunk of this.readChunks(reader)) {
      const text = new TextDecoder().decode(chunk);
      console.log("Chunk", text);
      // expect application/x-ndjson
      const parts = text.split("\n");
      for (const part of parts) {
        if (part.length === 0) continue;
        const response = JSON.parse(part);
        if (response.context) {
          localStorage.setItem("context", response.context);
        }
        consume(response);
      }
    }
  }
}


