import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface ContextState {
    context: string[];
    addContext: (context: string) => void;
    clearContext: () => void;
}

export const useContextStore = create<ContextState>()(
    persist(
        (set) => ({
            context: [],
            addContext: (context) =>
                set((s) => ({
                    context: [...s.context, context]
                })),
            clearContext: () => set({ context: [] })
        }),
        {
            name: "context-storage",
            storage: createJSONStorage(() => localStorage),
        }
    )
);