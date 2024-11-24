import { create } from "zustand";
import { v4 as uuidv4 } from 'uuid';
import { persist, createJSONStorage } from "zustand/middleware";

export interface Action {
    page: string;
    action: string;
    payload?: string;
    state: "started" | "completed" | "failed";
}

export interface SessionState {
    threadId: string;
    actions: Action[];
    lastAction?: Action;
    startAction: (page: string, action: string, payload?: string) => void;
    completeAction: () => void;
    failAction: () => void;
    resetSession: () => void;
    setThreadId: (threadId: string) => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      threadId: "",
      lastAction: undefined,
      actions: [],
      startAction: (page, action, payload) =>
        set((s) => ({
          session: s.threadId,
          actions: [
            ...s.actions,
            {
              page: page,
              action: action,
              payload: payload,
              state: "started",
            },
          ],
          lastAction: {
            page: page,
            action: action,
            payload: payload,
            state: "started",
          },
        })),
      completeAction: () =>
        set((state) => {
          if (state.actions.length === 0) return state;

          const last = state.actions[state.actions.length - 1];
          if (last.state !== "started") return state;
          else {
            return {
              session: state.threadId,
              actions: [
                ...state.actions,
                {
                  page: last.page,
                  action: last.action,
                  payload: last.payload,
                  state: "completed",
                },
              ],
              lastAction: {
                page: last.page,
                action: last.action,
                payload: last.payload,
                state: "completed",
              },
            };
          }
        }),
      failAction: () =>
        set((state) => {
          if (state.actions.length === 0) return state;

          const last = state.actions[state.actions.length - 1];
          if (last.state !== "started") return state;
          else {
            return {
              session: state.threadId,
              actions: [
                ...state.actions,
                {
                  page: last.page,
                  action: last.action,
                  state: "failed",
                },
              ],
              lastAction: {
                page: last.page,
                action: last.action,
                state: "failed",
              },
            };
          }
        }),
      resetSession: () =>
        set({ threadId: uuidv4(), actions: [], lastAction: undefined }),
      setThreadId: (threadId) => set({ threadId: threadId }),
    }),
    {
      name: "session-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);