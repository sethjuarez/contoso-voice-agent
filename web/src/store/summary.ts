import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface SummaryState {
  context: string;
  article: string;
  setArticle: (article: string) => void;
  streamArticle: (chunk: string) => void;
  setContext: (context: string) => void;
  clearContent: () => void;
}

export const useSummaryStore = create<SummaryState>()(
  persist(
    (set) => ({
      context: "",
      article: "",
      setArticle: (article) => set({ article: article }),
      streamArticle: (chunk) =>
        set((state) => {
          return {
            article: state.article + chunk,
          };
        }),
      setContext: (context) => set({ context: context }),
      clearContent: () => set({ context: "", article: "" }),
    }),
    {
      name: "summary-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
