import { useEffect, useRef, useState } from "react";
import { WS_ENDPOINT } from "@/store/endpoint"
import { useLocalStorage } from "@/store/uselocalstorage";
import type { User } from "@/store/user";
import { defaultConfiguration, type VoiceConfiguration } from "@/store/voice";
import type { Message } from "@/store/voice/voice-client";
import VoiceClient from "@/store/voice/voice-client";
import { ActionClient } from "@/socket/action";

export const useRealtime = (
  user: User,
  client: ActionClient,
  handleMessage: (serverEvent: Message) => Promise<void>,
) => {
  const { storedValue: settings } = useLocalStorage<VoiceConfiguration>(
    "voice-settings",
    defaultConfiguration
  );

  const [callState, setCallState] = useState<"idle" | "ringing" | "call">("idle");
  const [talking, setTalking] = useState(false);
  const voiceRef = useRef<VoiceClient | null>(null);

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
        handleMessage,
        setTalking
      );

      await voiceRef.current.start(settings.inputDeviceId);

      await voiceRef.current.send({
        type: "messages",
        payload: JSON.stringify(client.retrieveMessages()),
      });
      
      const message = {
        user: user!.name,
        threshold: settings.threshold,
        silence: settings.silence,
        prefix: settings.prefix,
      };

      await voiceRef.current.sendUserMessage(JSON.stringify(message));
      await voiceRef.current.sendCreateResponse();
      setCallState("call");
    }
  };

  const stopRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
      setCallState("idle");
    }
  };

  const toggleRealtime = async () => {
    if (callState === "idle") {
      await startRealtime();
    }
    if (callState === "call") {
      await stopRealtime();
    }
  };

  const sendRealtime = async (message: Message) => {
    if (voiceRef.current) {
      await voiceRef.current.send(message);
    }
  };

  return {
    startRealtime,
    stopRealtime,
    toggleRealtime,
    sendRealtime,
    talking,
    callState,
    setCallState
  };
};
