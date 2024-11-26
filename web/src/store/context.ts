import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface ContextState {
  context: string[];
  call: number;
  addContext: (context: string) => void;
  clearContext: () => void;
  setCallScore: (call: number) => void;
}

export const useContextStore = create<ContextState>()(
  persist(
    (set) => ({
      context: [],
      call: 0,
      addContext: (context) =>
        set((s) => ({
          context: [...s.context, context],
        })),
      clearContext: () => set({ call: 0, context: [] }),
      setCallScore: (call) => set({ call: call }),
    }),
    {
      name: "context-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
