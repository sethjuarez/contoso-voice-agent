import { Player, Recorder } from "@/audio";
import { Message } from "./types";
import { WebSocketClient } from "./websocket-client";

/**
 * VoiceClient handles real-time voice communication with the server.
 * 
 * This class manages:
 * - WebSocket connection for voice streaming
 * - Audio recording from user's microphone
 * - Audio playback of server responses
 * - Message handling between client/server
 * 
 * The flow is:
 * 1. Initialize audio recording and playback
 * 2. Connect WebSocket to server
 * 3. Stream audio data to server
 * 4. Handle server responses (audio/text)
 */
class VoiceClient {
  url: string | URL;
  socket: WebSocketClient<Message, Message> | null;
  player: Player | null;
  recorder: Recorder | null;
  handleServerMessage: (message: Message) => Promise<void>;

  /**
   * Create a new VoiceClient instance.
   * 
   * @param url - WebSocket server URL
   * @param handleServerMessage - Callback for handling non-audio server messages
   */
  constructor(
    url: string | URL,
    handleServerMessage: (message: Message) => Promise<void>
  ) {
    this.url = url;
    this.handleServerMessage = handleServerMessage;
    this.socket = null;
    this.player = null;
    this.recorder = null;
  }

  /**
   * Start the voice client session.
   * 
   * Initializes audio components and WebSocket connection.
   * 
   * @param deviceId - Optional audio input device ID
   */
  async start(deviceId: string | null = null) {
    console.log("Starting voice client");
    this.socket = new WebSocketClient<Message, Message>(this.url);

    // Initialize audio playback at 24kHz
    this.player = new Player();
    await this.player.init(24000);

    // Initialize audio recording with message handler
    this.recorder = new Recorder((buffer) => {
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
      this.socket!.send({ type: "audio", payload: base64 });
    });

    // Configure audio input settings
    let audio: object = {
        sampleRate: 24000,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
    };
    
    if (deviceId) {
      console.log("Using device:", deviceId);
      audio = { ...audio, deviceId: { exact: deviceId } };
    }

    console.log(audio);
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: audio,
    });
    
    this.recorder.start(stream);
    this.startResponseListener();
  }

  /**
   * Start listening for server responses.
   * 
   * Handles both audio data for playback and other message types
   * that are forwarded to the message handler.
   */
  async startResponseListener() {
    if (!this.socket) {
      return;
    }

    try {
      for await (const serverEvent of this.socket) {
        
        if (serverEvent.type === "audio") {
          // Handle audio responses by playing them
          const buffer = Uint8Array.from(atob(serverEvent.payload), (c) =>
            c.charCodeAt(0)
          ).buffer;
          this.player!.play(new Int16Array(buffer));
        } else if(serverEvent.type === "interrupt") {
          // Clear audio queue on interrupt
          this.player!.clear();
        } else {
          // Forward other messages to handler
          this.handleServerMessage(serverEvent);
        }
      }
    } catch (error) {
      if (this.socket) {
        console.error("Response iteration error:", error);
      }
    }
  }

  /**
   * Stop the voice client session.
   * 
   * Cleans up audio components and closes WebSocket.
   */
  async stop() {
    if (this.socket) {
      this.player?.clear();
      this.recorder?.stop();
      await this.socket.close();
    }
  }

  /**
   * Send a message to the server.
   * 
   * @param message - Message to send
   */
  async send(message: Message) {
    if (this.socket) {
      this.socket.send(message);
    }
  }

  /**
   * Send a user text message to the server.
   * 
   * @param message - Text message to send
   */
  async sendUserMessage(message: string) {
    this.send({ type: "user", payload: message });
  }

  /**
   * Request the server to generate a new response.
   */
  async sendCreateResponse() {
    this.send({ type: "interrupt", payload: "" });
  }
}

export default VoiceClient;
