/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-this-alias */

/**
 * Internal helper to send a message through a WebSocket.
 * @param socket - The WebSocket instance to send through
 * @param message - The message payload to send
 * @returns Promise that resolves when sent, rejects if socket not open
 */
function sendMessage(
  socket: WebSocket, 
  message: string | ArrayBufferLike | ArrayBufferView
): Promise<void> {
  if (socket.readyState !== WebSocket.OPEN) {
    return Promise.reject(new Error("Socket is not open"));
  }
  socket.send(message);
  return Promise.resolve();
}

/** Function type for resolving an iterator result */
type ResolveFn<T> = (value: IteratorResult<T>) => void;
/** Function type for rejecting with an error */
type RejectFn<E> = (reason: E) => void;

/**
 * Client for handling bidirectional WebSocket communication with automatic message queueing.
 * Implements AsyncIterable to allow for async iteration over received messages.
 * 
 * @typeParam U - Type of messages sent to the server
 * @typeParam D - Type of messages received from the server
 * 
 * @example
 * ```typescript
 * const client = new WebSocketClient<RequestMsg, ResponseMsg>("ws://server");
 * await client.send({type: "request"}); // Send message
 * 
 * for await (const msg of client) {
 *   console.log("Received:", msg); // Handle responses
 * }
 * ```
 */
export class WebSocketClient<U, D> implements AsyncIterable<D> {
  private socket: WebSocket;
  private connectedPromise: Promise<void>;
  private closedPromise: Promise<void> | undefined = undefined;
  private error: Error | undefined;
  private messageQueue: D[] = [];

  private receiverQueue: [ResolveFn<D>, RejectFn<Error>][] = [];
  private done: boolean = false;

  constructor(url: string | URL) {
    this.socket = new WebSocket(url);
    this.connectedPromise = new Promise(async (resolve, reject) => {
      this.socket.onopen = () => {
        this.socket.onmessage = this.getMessageHandler();
        this.closedPromise = new Promise((resolve) => {
          this.socket.onclose = this.getClosedHandler(resolve);
        });
        this.socket.onerror = (ev: Event) => this.handleError(ev as ErrorEvent);
        resolve();
      };
      this.socket.onerror = (event: Event) => {
        const errorEvent = event as ErrorEvent;
        this.error = errorEvent.error;
        reject(errorEvent);
      };
    });
  }

  private handleError(event: ErrorEvent) {
    this.error = event.error;
    while (this.receiverQueue.length > 0) {
      const [_, reject] = this.receiverQueue.shift()!;
      reject(event.error);
    }
  }

  private getClosedHandler(
    closeResolve: (_: void) => void
  ): (_: CloseEvent) => void {
    return (_: CloseEvent) => {
      this.done = true;
      while (this.receiverQueue.length > 0) {
        const [resolve, reject] = this.receiverQueue.shift()!;
        if (this.error) {
          reject(this.error);
        } else {
          resolve({ value: undefined, done: true });
        }
      }
      closeResolve();
    };
  }

  private getMessageHandler(): (event: MessageEvent) => void {
    const self = this;
    return (event: MessageEvent) => {
      const message = JSON.parse(event.data as string);
      if (self.receiverQueue.length > 0) {
        const [resolve, _] = self.receiverQueue.shift()!;
        resolve({ value: message, done: false });
      } else {
        self.messageQueue.push(message);
      }
    };
  }

  [Symbol.asyncIterator](): AsyncIterator<D> {
    return {
      next: (): Promise<IteratorResult<D>> => {
        if (this.error) {
          return Promise.reject(this.error);
        } else if (this.done) {
          return Promise.resolve({ value: undefined, done: true });
        } else if (this.messageQueue.length > 0) {
          const message = this.messageQueue.shift()!;
          return Promise.resolve({ value: message, done: false });
        } else {
          return new Promise((resolve, reject) => {
            this.receiverQueue.push([resolve, reject]);
          });
        }
      },
    };
  }

  /**
   * Sends a message to the WebSocket server.
   * Waits for the connection to be established first.
   * 
   * @param message - The message to send to the server
   * @throws Error if there was a connection error or the socket is closed
   * @returns Promise that resolves when the message is sent
   */
  async send(message: U): Promise<void> {
    await this.connectedPromise;
    if (this.error) {
      throw this.error;
    }
    const serialized = JSON.stringify(message);
    return sendMessage(this.socket, serialized);
  }

  /**
   * Closes the WebSocket connection if open.
   * Waits for pending operations to complete.
   * @returns Promise that resolves when the connection is fully closed
   */
  async close(): Promise<void> {
    await this.connectedPromise;
    if (this.done) {
      return;
    }
    this.socket.close();
    await this.closedPromise;
  }
}
