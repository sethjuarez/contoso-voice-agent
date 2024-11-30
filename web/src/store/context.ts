import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface ContextState {
  context: string[];
  suggestion: string[];
  call: number;
  addContext: (context: string) => void;
  clearContext: () => void;
  setCallScore: (call: number) => void;
  setSuggestion: (suggestion: string[]) => void;
  streamSuggestion: (chunk: string) => void;
}

export const useContextStore = create<ContextState>()(
  persist(
    (set) => ({
      context: [],
      suggestion: [],
      call: 0,
      addContext: (context) =>
        set((s) => ({
          context: [...s.context, context],
        })),
      clearContext: () => set({ call: 0, suggestion: [], context: [] }),
      setCallScore: (call) => set({ call: call }),
      setSuggestion: (suggestion) => set({ suggestion: suggestion }),
      streamSuggestion: (chunk: string) =>
        set((state) => {
          return { suggestion: [...state.suggestion, chunk] };
        }),
    }),
    {
      name: "context-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
