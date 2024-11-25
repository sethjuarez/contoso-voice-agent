import { create } from "zustand";
import { v4 as uuidv4 } from "uuid";
import { removeCachedBlob } from "./images";
import { persist, createJSONStorage } from "zustand/middleware";

export const AssistantName = "Wiry";

export interface Turn {
  name: string;
  avatar: string | null;
  image: string | null;
  message: string;
  status: "waiting" | "streaming" | "done" | "voice";
  type: "user" | "assistant";
}

export interface ChatState {
  threadId: string;
  open: boolean;
  turns: Turn[];
  message: string;
  currentImage: string | null;
  setOpen: (open: boolean) => void;
  setMessage: (message: string) => void;
  setCurrentImage: (image: string | null) => void;
  sendFullMessage: (turn: Turn) => void;
  sendMessage: (name: string, avatar: string) => void;
  addAssistantMessage: (
    name: string,
    message: string,
    avatar?: string,
    image?: string
  ) => void;
  startAssistantMessage: (
    name: string,
    avatar?: string,
    image?: string
  ) => void;
  streamAssistantMessage: (chunk: string) => void;
  completeAssistantMessage: () => void;
  resetChat: () => void;
  setThreadId: (threadId: string) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      threadId: uuidv4(),
      open: false,
      turns: [],
      message: "",
      currentImage: null,
      setOpen: (open) => set({ open: open }),
      setMessage: (message) => set({ message: message }),
      setCurrentImage: (image) => set({ currentImage: image }),
      sendFullMessage: (turn: Turn) =>
        set((state) => {
          if (!turn.message || turn.message.length === 0) return state;
          return {
            turns: [...state.turns, turn],
            message: "",
            currentImage: null,
          };
        }),
      sendMessage: (name, avatar) =>
        set((state) => {
          if (!state.message || state.message.length === 0) return state;
          return {
            turns: [
              ...state.turns,
              {
                name: name,
                avatar: avatar,
                image: state.currentImage,
                message: state.message,
                status: "done",
                type: "user",
              },
            ],
            message: "",
            currentImage: null,
          };
        }),
      addAssistantMessage: (name, message, avatar, image) =>
        set((state) => ({
          turns: [
            ...state.turns,
            {
              name: name,
              avatar: avatar || null,
              image: image || null,
              message: message,
              status: "done",
              type: "assistant",
            },
          ],
        })),
      startAssistantMessage: (name, avatar, image) =>
        set((state) => ({
          turns: [
            ...state.turns,
            {
              name: name,
              avatar: avatar || null,
              image: image || null,
              message: "",
              status: "waiting",
              type: "assistant",
            },
          ],
        })),
      streamAssistantMessage: (chunk) =>
        set((state) => {
          const turns = state.turns.slice(0, -1);
          let lastTurn = state.turns.slice(-1)[0];
          if (lastTurn.type === "assistant" && lastTurn.status === "waiting") {
            lastTurn.message = chunk;
            lastTurn.status = "streaming";
          } else {
            lastTurn = {
              name: lastTurn.name,
              avatar: lastTurn.avatar,
              image: lastTurn.image,
              message: chunk,
              status: "streaming",
              type: "assistant",
            };
          }
          return { turns: [...turns, lastTurn] };
        }),
      completeAssistantMessage: () =>
        set((state) => {
          const turns = state.turns.slice(0, -1);
          const lastTurn = state.turns.slice(-1)[0];
          if (
            lastTurn.type === "assistant" &&
            lastTurn.status === "streaming"
          ) {
            lastTurn.status = "done";
          }
          return { turns: [...turns, lastTurn] };
        }),
      resetChat: () =>
        set((state) => {
          // clear image cache
          state.turns.forEach((turn) => {
            if (turn.image) {
              removeCachedBlob(turn.image);
            }
          });
          if (state.currentImage) {
            removeCachedBlob(state.currentImage);
          }
          return { threadId: uuidv4(), turns: [], message: "", currentImage: null };
        }),
      setThreadId: (threadId) => set({ threadId: threadId }),
    }),
    {
      name: "chat-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);