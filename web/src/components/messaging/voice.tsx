"use client";
//import VoiceClient from "@/socket/voice-client";
import clsx from "clsx";
import styles from "./voice.module.css";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  FiPhone,
  FiPhoneCall,
  FiPhoneOff,
  FiSettings,
} from "react-icons/fi";
import { WS_ENDPOINT } from "@/store/endpoint";
import { Message } from "@/socket/types";
import VoiceClient from "@/socket/voice-client";
import { useSound } from "@/audio/useSound";
import { ContextState, useContextStore } from "@/store/context";
import usePersistStore from "@/store/usePersistStore";
import { ChatState, useChatStore } from "@/store/chat";
import {
  ActionClient,
  startSuggestionTask,
  suggestionRequested,
} from "@/socket/action";
import Content from "./content";
import { useUserStore } from "@/store/user";
import VoiceSettings from "./voicesettings";
import { GrClose } from "react-icons/gr";
import { getSettings } from "@/socket/settings";


const Voice = () => {
  const contentRef = useRef<string[]>([]);

  const [settings, setSettings] = useState<boolean>(false);

  const [callState, setCallState] = useState<"idle" | "ringing" | "call">(
    "idle"
  );

  const [suggestions, setSuggestions] = useState<boolean>(false);
  const suggestionsRef = useRef<boolean>(false);

  const { playSound, stopSound } = useSound("/phone-ring.mp3");

  const state = usePersistStore(useChatStore, (state) => state);
  const stateRef = useRef<ChatState | undefined>();

  const context = usePersistStore(useContextStore, (state) => state);
  const contextRef = useRef<ContextState | undefined>();

  const buttonRef = useRef<HTMLDivElement>(null);
  const settingsRef = useRef<HTMLDivElement>(null);
  const voiceRef = useRef<VoiceClient | null>(null);

  const user = usePersistStore(useUserStore, (state) => state.user);

  const handleServerMessage = async (serverEvent: Message) => {
    const client = new ActionClient(stateRef.current!, contextRef.current!);
    switch (serverEvent.type) {
      case "assistant":
        console.log("assistant:", serverEvent.payload);
        const messages = client.sendVoiceAssistantMessage(serverEvent.payload);
        console.log(suggestionsRef.current);
        if (!suggestionsRef.current) {
          const response = await suggestionRequested(messages);
          console.log("messages", messages, response);
          if (response && response.requested) {
            setSuggestions(true);
            suggestionsRef.current = true;
            const task = await startSuggestionTask(messages);
            for await (const chunk of task) {
              contentRef.current.push(chunk);
              client.streamSuggestion(chunk);
            }
            if (voiceRef.current) {
              await voiceRef.current.sendUserMessage(
                "The visual suggestions are ready."
              );
              await voiceRef.current.sendCreateResponse();
            }
          }
        }
        break;
      case "user":
        console.log("user:", serverEvent.payload);
        client.sendVoiceUserMessage(serverEvent.payload);

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
      const client = new ActionClient(stateRef.current!, contextRef.current!);
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
      await voiceRef.current.send({
        type: "messages",
        payload: JSON.stringify(client.retrieveMessages()),
      });

      const voiceSettings = getSettings();
      const message = {
        user: user?.name || "Seth",
        ...voiceSettings,
      }

      await voiceRef.current.sendUserMessage(JSON.stringify(message));
      await voiceRef.current.sendCreateResponse();
    }
  };

  const stopRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
    }
  };

  const toggleSettings = () => {
    setSettings(!settings);
    settingsRef.current?.classList.toggle(styles.settingsOn);
  };

  const startCall = useCallback(async () => {
    console.log("Starting call");
    setCallState("ringing");
    playSound();
  }, [playSound]);

  const answerCall = async () => {
    console.log("Answering call");
    setCallState("call");
    stopSound();
    buttonRef.current?.classList.remove(styles.callRing);
    await startRealtime();
  };

  const hangupCall = async () => {
    console.log("Hanging up call");
    setCallState("idle");
    stopSound();
    await stopRealtime();
  };

  useEffect(() => {
    if (context) {
      contextRef.current = context;
    }
    if (state) {
      stateRef.current = state;
    }
  }, [context, state]);

  useEffect(() => {
    if (contextRef.current && contextRef.current.call >= 5) {
      contextRef.current.setCallScore(0);
      startCall();
    }
  }, [contextRef.current?.call, startCall]);

  const onCloseSuggestions = () => {
    setSuggestions(false);
    suggestionsRef.current = false;
  };

  return (
    <div className={styles.voice}>
      {suggestions && (
        <Content
          suggestions={contentRef.current}
          onClose={onCloseSuggestions}
        />
      )}
      <div className={styles.voiceControl}>
        {callState === "idle" && (
          <div className={styles.voiceButton} onClick={startCall}>
            <FiPhone size={32} />
          </div>
        )}
        {callState !== "idle" && (
          <>
            <div
              className={clsx(styles.callButton, styles.callRing)}
              ref={buttonRef}
              onClick={answerCall}
            >
              <FiPhoneCall size={32} />
            </div>
            <div className={styles.callHangup} onClick={hangupCall}>
              <FiPhoneOff size={32} />
            </div>
          </>
        )}
        <div
          className={styles.settingsButton}
          ref={settingsRef}
          onClick={toggleSettings}
        >
          {settings ? <GrClose size={24} /> : <FiSettings size={32} />}
        </div>
      </div>
      {settings && <VoiceSettings />}
    </div>
  );
};

export default Voice;
