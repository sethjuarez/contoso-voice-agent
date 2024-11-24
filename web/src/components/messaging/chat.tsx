"use client";
import Message from "./message";
import styles from "./chat.module.css";
import { useEffect, useRef, useState } from "react";
import { GrPowerReset, GrClose, GrBeacon } from "react-icons/gr";
import { HiOutlineChatBubbleLeftRight } from "react-icons/hi2";
import { HiOutlinePaperAirplane } from "react-icons/hi2";
//typescript-eslint.io/rules/no-unused-vars
import { User, useUserStore } from "@/store/user";
import { AssistantName, ChatState, Turn, useChatStore } from "@/store/chat";
import usePersistStore from "@/store/usePersistStore";
import FileImagePicker from "./fileimagepicker";
import { fetchCachedImage, removeCachedBlob } from "@/store/images";
import VideoImagePicker from "./videoimagepicker";
import { WS_ENDPOINT } from "@/store/endpoint";
import {
  Action,
  Assistant,
  Context,
  SocketMessage,
  SocketServer,
} from "@/store/socket";
import { SessionState, useSessionStore } from "@/store/session";
import { ContextState, useContextStore } from "@/store/context";
import clsx from "clsx";
import { useSummaryStore } from "@/store/summary";

interface ChatOptions {
  video?: boolean;
  file?: boolean;
}
type Props = {
  options?: ChatOptions;
};

const Chat = ({ options }: Props) => {
  /** Socket */
  const server = useRef<SocketServer | null>(null);
  const [connected, setConnected] = useState<boolean>(false);

  /** STORE */
  const [currentImage, setCurrentImage] = useState<string | null>(null);
  const state = usePersistStore(useChatStore, (state) => state);
  const stateRef = useRef<ChatState | undefined>();

  const session = usePersistStore(useSessionStore, (state) => state);
  const sessionRef = useRef<SessionState | undefined>();

  const user = useUserStore((state) => state.user);
  const setUser = useUserStore((state) => state.setUser);

  const context = usePersistStore(useContextStore, (state) => state);
  const contextRef = useRef<ContextState | undefined>();

  const summary = usePersistStore(useSummaryStore, (state) => state);

  /** Startup */
  useEffect(() => {
    if (!user) {
      const fetchUser = async () => {
        // TODO: Replace with EasyAuth
        //const response = await fetch("/auth");
        //const data = await response.json();
        //const user = data as User;
        const u: User = {
          name: "Seth Juarez",
          email: "seth.juarez@microsoft.com",
          image: "/people/sethjuarez.jpg",
        };
        setUser(u.name, u.email, u.image);
      };

      fetchUser();
    }

    if (
      !server.current &&
      session &&
      session?.threadId &&
      session?.threadId.length > 0
    ) {
      createSocket(session?.threadId);
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.threadId]);



  /** Current State */
  useEffect(() => {
    stateRef.current = state;

    if (state && state.currentImage) {
      fetchCachedImage(state.currentImage, setCurrentImage).then(() => {
        scrollChat();
      });
    }
  }, [state]);

  /** Current Session */
  useEffect(() => {
    sessionRef.current = session;

    // did we just change location?
    // if so, we need to complete the action
    if (
      session &&
      session.lastAction &&
      session.lastAction.action === "move" &&
      session.lastAction.state === "started" &&
      session.lastAction.payload
    ) {
      const location = JSON.parse(session.lastAction.payload);
      if (window.location.href.endsWith(location.href)) {
        session.completeAction();
      }
    }
  }, [session]);

  /** Current Context */
  useEffect(() => {
    contextRef.current = context;
  }, [context]);

  /** Send */
  const sendMessage = async () => {
    if (stateRef.current && contextRef.current) {
      // get current message
      const turn: Turn = {
        name: user?.name || "Seth Juarez",
        avatar: user?.image || "/people/sethjuarez.jpg",
        image: stateRef.current.currentImage,
        message: stateRef.current.message,
        status: "done",
        type: "user",
      };

      // can replace with current user
      stateRef.current.sendMessage(
        user?.name || "Seth Juarez",
        user?.image || "/people/sethjuarez.jpg"
      );
      // reset image
      setCurrentImage(null);

      // process on server
      //execute(turn);
      if (server.current && server.current.ready) {
        await server.current.sendTurn(turn, contextRef.current.context);
      }
    }
  };

  /** Events */
  const serverCallback = (data: SocketMessage) => {
    //console.log("Server Response:", data);

    // assistant messaging work
    if (stateRef.current && data.type === "assistant") {
      const payload = data.payload as Assistant;
      
      if (payload.state === "start") {
        console.log("Assistant Payload", payload);
        stateRef.current.startAssistantMessage(AssistantName);
      } else if (payload.state === "stream") {
        
        stateRef.current.streamAssistantMessage(payload.payload || "");
      } else if (payload.state === "complete") {
        console.log("Assistant Payload", payload);
        stateRef.current.completeAssistantMessage();
      } else if (payload.state === "full") {
        stateRef.current.addAssistantMessage(
          AssistantName,
          payload.payload || ""
        );
      }
    } else if (contextRef.current && data.type === "context") {
      const payload = data.payload as Context;
      console.log("Context Payload", payload);
      if (payload.type === "user" && contextRef.current) {
        contextRef.current.addContext(payload.payload);
      } else if (payload.type === "action") {
        localStorage.setItem("actionContext", payload.payload);
      }
    } else if (sessionRef.current && data.type === "action") {
      const payload = data.payload as Action;
      console.log("Action Payload", payload);
      sessionRef.current.startAction(
        window.location.pathname,
        payload.name,
        payload.arguments
      );
      if (payload.name === "move") {
        const location = JSON.parse(payload.arguments);
        // change location
        window.location.href = location.href;
      } else if (payload.name === "console") {
        const args = JSON.parse(payload.arguments);
        console.log(args);
        sessionRef.current.completeAction();
      } else if (payload.name === "thread") {
        const args = JSON.parse(payload.arguments);
        sessionRef.current.setThreadId(args.thread);
      }
    }
  };

  const manageConnection = () => {
    if (server.current && server.current.ready) {
      server.current.close();
      server.current = null;
    } else {
      if (sessionRef.current && sessionRef.current.threadId) {
        //console.log("Creating Socket " + sessionRef.current.threadId);
        createSocket(sessionRef.current.threadId);
      }
    }
  };

  const createSocket = (threadId: string) => {
    console.log("Starting Socket (" + threadId + ")");
    const endpoint = WS_ENDPOINT.endsWith("/")
      ? WS_ENDPOINT
      : WS_ENDPOINT + "/";
    server.current = new SocketServer(endpoint + "api/concierge/ws", threadId,  () => setConnected(true), () => setConnected(false));;
    server.current.addListener("chat", serverCallback);
  };

  const clear = () => {
    state && state.clearMessages();
    session && session.resetSession();
    context && context.clearContext();
    summary && summary.clearContent();
    if(server.current && server.current.ready)
    {
      server.current.close();
      server.current = null;
    }
    clearImage();
  };

  const clearImage = () => {
    // remove image from cache
    if (state?.currentImage) {
      removeCachedBlob(state?.currentImage);
    }
    state && state.setCurrentImage(null);
    setCurrentImage(null);
  };

  /** Updates */
  const chatDiv = useRef<HTMLDivElement>(null);

  const scrollChat = () => {
    setTimeout(() => {
      if (chatDiv.current) {
        chatDiv.current.scrollTo({
          top: chatDiv.current.scrollHeight,
          behavior: "smooth",
        });
      }
    }, 10);
  };

  useEffect(() => {
    scrollChat();
  }, [state?.turns.length, state?.currentImage]);

  return (
    <>
      <div className={state?.open ? styles.overlay : styles.hidden}></div>
      <div className={styles.chat}>
        {state && state?.open && (
          <div className={styles.chatWindow}>
            <div className={styles.chatHeader}>
              <GrPowerReset
                size={18}
                className={styles.chatIcon}
                onClick={() => clear()}
              />
              <div className={"grow"} />
              <div>
                <GrBeacon
                  size={18}
                  className={clsx(
                    styles.chatIcon,
                    connected ? styles.connected : styles.disconnected
                  )}
                  onClick={() => manageConnection()}
                />
              </div>
              <div>
                <GrClose
                  size={18}
                  className={styles.chatIcon}
                  onClick={() => state && state.setOpen(false)}
                />
              </div>
            </div>
            {/* chat section */}
            <div className={styles.chatSection} ref={chatDiv}>
              <div className={styles.chatMessages}>
                {state &&
                  state.turns.map((turn, index) => (
                    <Message key={index} turn={turn} notify={scrollChat} />
                  ))}
              </div>
            </div>
            {/* image section */}
            {currentImage && (
              <div className={styles.chatImageSection}>
                <img
                  src={currentImage}
                  className={styles.chatImage}
                  alt="Current Image"
                  onClick={() => clearImage()}
                />
              </div>
            )}
            {/* chat input section */}
            <div className={styles.chatInputSection}>
              <input
                id="chat"
                name="chat"
                type="text"
                title="Type a message"
                value={state ? state.message : ""}
                onChange={(e) => state && state.setMessage(e.target.value)}
                onKeyUp={(e) => {
                  if (e.code === "Enter") sendMessage();
                }}
                className={styles.chatInput}
              />
              {options && options.file && (
                <FileImagePicker setCurrentImage={state.setCurrentImage} />
              )}
              {options && options.video && (
                <VideoImagePicker setCurrentImage={state.setCurrentImage} />
              )}
              <button
                type="button"
                title="Send Message"
                className={"button"}
                onClick={sendMessage}
              >
                <HiOutlinePaperAirplane size={24} className={"buttonIcon"} />
              </button>
            </div>
          </div>
        )}
        <div
          className={styles.chatButton}
          onClick={() => {
            state && state.setOpen(!state.open);
            scrollChat();
          }}
        >
          {state?.open ? (
            <GrClose size={24} />
          ) : (
            <HiOutlineChatBubbleLeftRight size={32} />
          )}
        </div>
      </div>
    </>
  );
};

export default Chat;
