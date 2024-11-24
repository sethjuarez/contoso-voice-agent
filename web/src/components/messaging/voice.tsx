"use client";
//import VoiceClient from "@/socket/voice-client";
import styles from "./voice.module.css";
import { useRef, useState } from "react";
import { HiOutlinePhone } from "react-icons/hi2";
import { WS_ENDPOINT } from "@/store/endpoint";
import { WebSocketClient } from "@/socket/websocket-client";
import { Player, Recorder } from "@/audio";
import { Message } from "@/socket/types";

const Voice = () => {
  const [listening, setListening] = useState<boolean>(false);
  const buttonRef = useRef<HTMLDivElement>(null);
  const socket = useRef<WebSocketClient<Message, Message> | null>(null);
  const player = useRef<Player | null>(null);
  const recorder = useRef<Recorder | null>(null);

  const startResponseListener = async () => {
    if (!socket.current) return;

    try {
      for await (const serverEvent of socket.current) {
        handleServerMessage(serverEvent);
      }
    } catch (error) {
      if (socket.current) {
        console.error("Response iteration error:", error);
      }
    }
  };

  const handleServerMessage = async (serverEvent: Message) => {
    switch (serverEvent.type) {
      case "assistant":
        console.log("assistant:", serverEvent.payload);
        break;
      case "user":
        console.log("user:", serverEvent.payload);
        break;
      case "console":
        console.log(serverEvent.payload);
        break;
      case "audio":
        const buffer = Uint8Array.from(atob(serverEvent.payload), (c) =>
          c.charCodeAt(0)
        ).buffer;
        player.current?.play(new Int16Array(buffer));
        break;
    }
  };

  const startRealtime = async () => {
    if (!socket.current) {
      console.log("Starting realtime");
      const endpoint = WS_ENDPOINT.endsWith("/")
        ? WS_ENDPOINT
        : WS_ENDPOINT + "/";
      socket.current = new WebSocketClient<Message, Message>(
        `${endpoint}/api/voice`
      );
      player.current = new Player();
      await player.current.init(24000);

      recorder.current = new Recorder((buffer) => {
        const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
        socket.current?.send({ type: "audio", payload: base64 });
      });
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 24000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          deviceId: {
            exact:
              "b80b999d47b5ff3844a83ecbabe57d0425018127d886267a78fe93d3cee6e670",
          },
        },
      });

      const devices = await navigator.mediaDevices.enumerateDevices();
      console.log(devices);
      recorder.current.start(stream);

      startResponseListener();
    }
  };

  const stopRealtime = async () => {
    if (socket.current) {
      console.log("Stopping realtime");
      player.current?.clear();
      recorder.current?.stop();
      await socket.current.close();
      socket.current = null;
    }
  };

  const toggleRealtime = () => {
    setListening(!listening);
    if (listening) {
      stopRealtime();
    } else {
      startRealtime();
    }
    // toggle css class
    buttonRef.current?.classList.toggle(styles.voiceOn);
  };

  return (
    <div className={styles.voice}>
      <div
        className={styles.voiceButton}
        ref={buttonRef}
        onClick={toggleRealtime}
      >
        <HiOutlinePhone size={32} />
      </div>
    </div>
  );
};

export default Voice;
