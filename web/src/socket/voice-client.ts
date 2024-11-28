import { Player, Recorder } from "@/audio";
import { Message } from "./types";
import { WebSocketClient } from "./websocket-client";

class VoiceClient {
  url: string | URL;
  socket: WebSocketClient<Message, Message> | null;
  player: Player | null;
  recorder: Recorder | null;
  handleServerMessage: (message: Message) => Promise<void>;

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

  async start(deviceId: string | null = null) {
    console.log("Starting voice client");
    this.socket = new WebSocketClient<Message, Message>(this.url);

    this.player = new Player();

    await this.player.init(24000);

    this.recorder = new Recorder((buffer) => {
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
      this.socket!.send({ type: "audio", payload: base64 });
    });
    const constraints: MediaStreamConstraints = {
      audio: {
        sampleRate: 24000,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    };
    
    if (deviceId) {
      console.log("Using device:", deviceId);
      constraints.audio = {...constraints, deviceId: { exact: deviceId }};
    }

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    this.recorder.start(stream);
    this.startResponseListener();
  }

  async startResponseListener() {
    if (!this.socket) {
      return;
    }

    try {
      for await (const serverEvent of this.socket) {
        
        if (serverEvent.type === "audio") {
          // handle audio case internally
          const buffer = Uint8Array.from(atob(serverEvent.payload), (c) =>
            c.charCodeAt(0)
          ).buffer;
          this.player!.play(new Int16Array(buffer));
        } else if(serverEvent.type === "interrupt") {
          // handle interrupt case internally
          this.player!.clear();
        } else {
          this.handleServerMessage(serverEvent);
        }
      }
    } catch (error) {
      if (this.socket) {
        console.error("Response iteration error:", error);
      }
    }
  }

  async stop() {
    if (this.socket) {
      this.player?.clear();
      this.recorder?.stop();
      await this.socket.close();
    }
  }
}

export default VoiceClient;
