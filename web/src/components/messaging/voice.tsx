"use client";
//import VoiceClient from "@/socket/voice-client";
import styles from "./voice.module.css";
import { useRef, useState } from "react";
import {
  HiOutlinePhone,
  HiOutlineArrowRightOnRectangle,
  HiOutlineArrowLeftOnRectangle,
} from "react-icons/hi2";
import { WS_ENDPOINT } from "@/store/endpoint";
import { WebSocketClient } from "@/socket/websocket-client";
import { Player, Recorder } from "@/audio";
import { Message } from "@/socket/types";
import VoiceInput from "./voiceinput";

const Voice = () => {
  const [listening, setListening] = useState<boolean>(false);
  const [settings, setSettings] = useState<boolean>(false);

  const buttonRef = useRef<HTMLDivElement>(null);
  const settingsRef = useRef<HTMLDivElement>(null);
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
        ? WS_ENDPOINT.slice(0, -1)
        : WS_ENDPOINT;
      socket.current = new WebSocketClient<Message, Message>(
        `${endpoint}/api/voice`
      );
      player.current = new Player();
      await player.current.init(24000);

      recorder.current = new Recorder((buffer) => {
        const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
        socket.current?.send({ type: "audio", payload: base64 });
      });

      const device = localStorage.getItem("selected-audio-device");
      let constraints: MediaStreamConstraints;
      if (device) {
        const parsedDevice = JSON.parse(device);
        console.log("Using device:", parsedDevice);
        constraints = {
          audio: {
            sampleRate: 24000,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            deviceId: { exact: parsedDevice.deviceId },
          },
        };
      } else {
        console.log("Using default device");
        constraints = {
          audio: {
            sampleRate: 24000,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
        };
      }
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
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

  const toggleSettings = () => {
    setSettings(!settings);
    settingsRef.current?.classList.toggle(styles.settingsOn);
  }

  return (
    <div className={styles.voice}>
      <div
        className={styles.voiceButton}
        ref={buttonRef}
        onClick={toggleRealtime}
      >
        <HiOutlinePhone size={32} />
      </div>
      <div
        className={styles.settingsButton}
        ref={settingsRef}
        onClick={toggleSettings}
      >
        {settings ? (
          <HiOutlineArrowLeftOnRectangle size={32} />
        ) : (
          <HiOutlineArrowRightOnRectangle size={32} />
        )}
      </div>
      {settings && <VoiceInput />}
    </div>
  );
};

export default Voice;
