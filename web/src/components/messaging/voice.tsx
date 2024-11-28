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
import { Message } from "@/socket/types";
import VoiceInput from "./voiceinput";
import VoiceClient from "@/socket/voice-client";

const Voice = () => {
  const [listening, setListening] = useState<boolean>(false);
  const [settings, setSettings] = useState<boolean>(false);

  const buttonRef = useRef<HTMLDivElement>(null);
  const settingsRef = useRef<HTMLDivElement>(null);
  const voiceRef = useRef<VoiceClient | null>(null);

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
    }
  };

  const startRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
    }

    if (!voiceRef.current) {
      const endpoint = WS_ENDPOINT.endsWith("/")
        ? WS_ENDPOINT.slice(0, -1)
        : WS_ENDPOINT;

      voiceRef.current = new VoiceClient(
        `${endpoint}/api/voice`,
        handleServerMessage
      );

      const device = localStorage.getItem("selected-audio-device");
      let deviceId: string | null = null;
      if (device) {
        const parsedDevice = JSON.parse(device);
        console.log("Using device:", parsedDevice);
        deviceId = parsedDevice.deviceId;
      }
      await voiceRef.current.start(deviceId);
    }
  };

  const stopRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
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
